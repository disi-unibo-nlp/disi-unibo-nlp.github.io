import os
import yaml
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# GitHub raw URL base
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/AI/"
# GitHub repo page where files are listed
GITHUB_PAGE = "https://github.com/ccfddl/ccf-deadlines/tree/main/conference/AI"
# Output YAML file
OUTPUT_FILE = "docs/_data/conferences.yml"
# Get the current year dynamically
CURRENT_YEAR = datetime.now().year

def get_conference_files2():
    """Scrapes the GitHub AI directory to get the list of YAML files."""
    response = requests.get(GITHUB_PAGE)
    if response.status_code != 200:
        print("❌ Failed to fetch the directory listing.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    files = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".yaml") or href.endswith(".yml"):
            filename = href.split("/")[-1]
            files.append(filename)

    print(f"✅ Found {len(files)} conference files.")
    return files

def get_conference_files():
    """Usa GitHub API per ottenere la lista dei file YAML nella directory AI."""
    api_url = "https://api.github.com/repos/ccfddl/ccf-deadlines/contents/conference/AI"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to fetch the directory listing via API.")
        return []
    
    files = []
    for item in response.json():
        if item["name"].endswith(".yaml") or item["name"].endswith(".yml"):
            files.append(item["name"])

    print(f"✅ Found {len(files)} conference files.")
    return files


def download_yaml_file(filename):
    """Downloads an individual YAML file from GitHub."""
    url = GITHUB_RAW_BASE + filename
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            return yaml.safe_load(response.text)
        except yaml.YAMLError as e:
            print(f"⚠️ Error parsing YAML file {filename}: {e}")
            return None
    else:
        print(f"❌ Failed to download {filename}")
        return None

def process_conferences():
    """Fetches, filters, and restructures conference data while avoiding duplicates."""
    files = get_conference_files()
    unique_conferences = {}

    for file in files:
        data = download_yaml_file(file)
        if data:
            # Ensure we are dealing with a dictionary
            if isinstance(data, dict):
                data = [data]

            for conf in data:
                if "confs" in conf and isinstance(conf["confs"], list):
                    #print(f"🔍 {conf['title']} has {len(conf['confs'])} entries")
                    # Filter to keep only the most recent year's conference
                    latest_conf = max(conf["confs"], key=lambda c: c["year"])

                    # Ensure no duplicate entries based on the conference ID
                    if latest_conf["id"] not in unique_conferences:
                        unique_conferences[latest_conf["id"]] = {
                            "title": conf["title"],
                            "description": conf["description"],
                            "sub": conf["sub"],
                            "rank": conf["rank"],
                            "dblp": conf["dblp"],
                            "year": latest_conf["year"],  # Moving year to the top level
                            "id": latest_conf["id"],
                            "link": latest_conf["link"],
                            "timezone": latest_conf["timezone"],
                            "date": latest_conf["date"],
                            "place": latest_conf["place"],
                            "abstract_deadline": latest_conf["timeline"][0].get("abstract_deadline", "N/A"),
                            "deadline": latest_conf["timeline"][0].get("deadline", "N/A"),
                        }
                else:
                    print(f"⚠️ Missing or malformed 'confs' in file: {conf.get('title', 'Unknown')}")

    # Convert dictionary back to a list and sort by deadline
    sorted_conferences = sorted(unique_conferences.values(), key=lambda x: x["deadline"])
    
    #os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    print("📁 Saving to:", os.path.abspath(OUTPUT_FILE))

    print(f"🔍 sorted_conferences contiene {len(sorted_conferences)} elementi")
    if len(sorted_conferences) > 0:
        print("📄 Esempio primo elemento:", sorted_conferences[0])
    else:
        print("⚠️ Nessuna conferenza valida trovata")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump({"conferences": sorted_conferences}, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Processed and saved {len(sorted_conferences)} unique conferences into {OUTPUT_FILE}")

if __name__ == "__main__":
    process_conferences()
