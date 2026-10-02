#!/usr/bin/env python3
"""Generate a single Jekyll data file from AMS Laurea and local exceptions."""
import argparse
from datetime import date
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import yaml

DOCS = Path(__file__).resolve().parents[1]
TYPES = {'THEL': 'bachelor', 'THELM': 'master'}

def person_name(person):
    return ' '.join(str(person.get(k) or '').strip() for k in ('given', 'family')).strip()


def normalize(record):
    ident = str(int(record['eprintid']))
    kind = next((TYPES[t] for t in record.get('thesistype', []) if t in TYPES), None)
    if kind is None:
        raise ValueError(f'Unsupported thesis type for AMS {ident}')
    discussed = date.fromisoformat(record['discussion_date'])
    creators = record.get('creators') or []
    names = [person_name(p['name']) for p in creators]
    supervisor = person_name(record.get('relatore') or {})
    title = str(record.get('title') or '').strip()
    if not title or not names or not all(names) or not supervisor:
        raise ValueError(f'Incomplete metadata for AMS {ident}')
    keywords = record.get('keywords') or ''
    keywords = [x.strip() for x in re.split(r'[,;]', keywords) if x.strip()]
    co = [person_name(p) for p in record.get('correlatore_multi', [])]
    result = dict(ams_id=int(ident), type=kind, title=title,
                  candidate=', '.join(names), supervisor=supervisor,
                  month=discussed.month, year=discussed.year,
                  discussion_date=discussed.isoformat(),
                  sort_date=discussed.isoformat(),
                  link=f'https://amslaurea.unibo.it/id/eprint/{ident}/',
                  abstract=str(record.get('abstract') or '').strip(),
                  keywords=keywords, co_supervisors=[n for n in co if n])
    return result


def download(year):
    query = urllib.parse.urlencode({'view': 'relatore',
        'values': f'Moro=3AGianluca=3A=3A/{year}', 'format': 'JSON',
        '_action_export_redir': 'Esporta'})
    request = urllib.request.Request('https://amslaurea.unibo.it/cgi/exportview?' + query,
                                     headers={'User-Agent': 'UniboNLP-Theses/1.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = json.load(response)
            if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
                raise ValueError(f'Unexpected JSON structure for {year}')
            if not data:
                print(f'No AMS records for {year}; existing local theses are retained', file=sys.stderr)
            return data
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def download_id(ident):
    ident = int(ident)
    url = f'https://amslaurea.unibo.it/cgi/export/eprint/{ident}/JSON/amslaurea-eprint-{ident}.js'
    request = urllib.request.Request(url, headers={'User-Agent': 'UniboNLP-Theses/2.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = json.load(response)
            if isinstance(raw, list):
                if len(raw) != 1:
                    raise ValueError(f'Unexpected export for AMS {ident}')
                raw = raw[0]
            if int(raw['eprintid']) != ident:
                raise ValueError(f'ID mismatch for AMS {ident}')
            return raw
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def canonical(value):
    value = unicodedata.normalize('NFKD', str(value)).casefold()
    return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))


def validate(row):
    if not isinstance(row, dict) or not all(row.get(k) for k in ('candidate', 'title', 'supervisor')):
        raise ValueError('Incomplete thesis metadata')
    if row.get('type') not in ('bachelor', 'master'):
        raise ValueError(f'Invalid thesis type: {row.get("candidate")}')
    date(int(row['year']), int(row['month']), 1)
    if row.get('discussion_date'):
        discussed = date.fromisoformat(str(row['discussion_date']))
        if discussed.year != int(row['year']) or discussed.month != int(row['month']):
            raise ValueError('Conflicting discussion date')
    if row.get('link') and urllib.parse.urlsplit(row['link']).scheme not in ('http', 'https'):
        raise ValueError('Invalid thesis link')
    return row


def matching_ids(manual, official):
    # Require a unique author/year/degree and a strongly matching title.
    return [ident for ident, row in official.items()
            if canonical(row['candidate']) == canonical(manual['candidate'])
            and int(row['year']) == int(manual['year'])
            and row['type'] == manual['type']
            and SequenceMatcher(None, canonical(row['title']), canonical(manual['title'])).ratio() >= .85]


def assemble(fresh, previous, local, excluded=()):
    excluded = {int(x) for x in excluded}
    official = {}
    # Keep previously imported AMS entries if the server temporarily omits them.
    # Manual entries are read only from the local file, never from the output cache.
    for row in previous:
        if row.get('ams_id') is not None:
            ident = int(row['ams_id'])
            if ident in official:
                raise ValueError(f'Duplicate cached AMS ID {ident}')
            official[ident] = dict(validate(row))
    for row in fresh:
        validate(row)
        official[int(row['ams_id'])] = dict(row)
    official = {ident: row for ident, row in official.items() if ident not in excluded}
    overrides = {int(k): v for k, v in (local.get('overrides') or {}).items()}
    result = []
    local_ids = set()
    for original in local.get('manual') or []:
        row = dict(validate(original))
        local_id = row.get('local_id')
        if not local_id or local_id in local_ids:
            raise ValueError('Missing or duplicate local thesis ID')
        local_ids.add(local_id)
        ids = matching_ids(row, official)
        if len(ids) > 1:
            raise ValueError(f'Ambiguous manual association: {row["candidate"]}')
        if len(ids) == 1:
            # A formerly unpublished thesis is now on AMS: do not show it twice.
            ident = ids[0]
            extra = {k: v for k, v in row.items() if k not in {
                'local_id', 'type', 'title', 'candidate', 'supervisor', 'month', 'year',
                'link', 'co_supervisors', 'discussion_date', 'sort_date', 'source', 'abstract', 'keywords'}}
            official[ident].update(extra)
        else:
            row['source'] = 'local'
            row['sort_date'] = row.get('discussion_date') or date(int(row['year']), int(row['month']), 1).isoformat()
            result.append(row)
    for ident, row in official.items():
        correction = overrides.get(ident) or {}
        if not isinstance(correction, dict):
            raise ValueError(f'Invalid override for AMS {ident}')
        if {'ams_id', 'local_id', 'source'} & correction.keys():
            raise ValueError(f'Override cannot change identity for AMS {ident}')
        row.update(correction)
        row['source'] = 'ams'
        # The ISO date controls ordering, including corrected metadata.
        row['sort_date'] = row.get('discussion_date') or date(int(row['year']), int(row['month']), 1).isoformat()
        for key in list(row):
            if re.fullmatch(r'co-supervisor\d+', key):
                del row[key]
        result.append(validate(row))
    return sorted(result, key=lambda r: (r['sort_date'], r['candidate']), reverse=True)


def load_yaml(path, default):
    if not path.exists():
        return default
    value = yaml.safe_load(path.read_text(encoding='utf-8'))
    return value if value is not None else default


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs', type=Path, default=DOCS)
    parser.add_argument('--year', type=int, action='append')
    parser.add_argument('--from-json', type=Path, help='Offline raw AMS JSON export')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    data_dir = args.docs / '_data'
    settings = load_yaml(data_dir / 'theses_import.yml', {})
    local = load_yaml(data_dir / 'theses_local.yml', {})
    output = data_dir / 'theses.yml'
    previous = load_yaml(output, [])
    if not isinstance(settings, dict) or not isinstance(local, dict) or not isinstance(previous, list):
        raise ValueError('Invalid thesis configuration or data file')
    years = args.year or list(range(int(settings.get('first_year', 2021)), date.today().year + 1))
    if not years:
        raise ValueError('No import years configured')
    raw = json.loads(args.from_json.read_text(encoding='utf-8')) if args.from_json else [r for y in years for r in download(y)]
    if not isinstance(raw, list):
        raise ValueError('AMS export must be a list')
    if not args.from_json:
        raw += [download_id(ident) for ident in settings.get('additional_ids', [])]
    fresh = [normalize(r) for r in raw]
    rows = assemble(fresh, previous, local, settings.get('excluded_ids', []))
    text = '# Generated by docs/scripts/fetch_theses.py. Edit theses_local.yml for exceptions.\n' + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=1000)
    changed = not output.exists() or output.read_text(encoding='utf-8') != text
    if changed and not args.dry_run:
        data_dir.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix('.yml.tmp')
        temporary.write_text(text, encoding='utf-8')
        temporary.replace(output)
    ams_count = sum(r.get('source') == 'ams' for r in rows)
    print(f'{ams_count} AMS theses + {len(rows) - ams_count} local exceptions; ' +
          ('would update' if changed and args.dry_run else 'updated' if changed else 'unchanged'))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as error:
        print(f'Thesis import failed: {error}', file=sys.stderr)
        sys.exit(1)
