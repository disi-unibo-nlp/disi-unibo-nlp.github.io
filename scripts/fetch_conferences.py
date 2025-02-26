import os
import yaml
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from datetime import datetime

# GitHub raw URL base
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/ccfddl/ccf-deadlines/main/conference/AI/"

# GitHub repo page where files are listed
GITHUB_PAGE = "https://github.com/ccfddl/ccf-deadlines/tree/main/conference/AI"

# Output YAML file
OUTPUT_FILE = "docs/_data/conferences.yml"

def get_conference_files():
    """Scrapes the GitHub AI directory to get the list of YAML files."""
    response = requests.get(GITHUB_PAGE)
    if response.status_code != 200:
        print("Failed to fetch the directory listing.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    files = []
    
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".yaml") or href.endswith(".yml"):
            filename = href.split("/")[-1]
            files.append(filename)
    
    return files

def download_yaml_file(filename):
    """Downloads an individual YAML file from GitHub."""
    url = GITHUB_RAW_BASE + filename
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            return yaml.safe_load(response.text)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {filename}: {e}")
            return None
    else:
        print(f"Failed to download {filename}")
        return None

def merge_conferences():
    """Fetches, filters, and merges all 2025 conferences into a single YAML file."""
    files = get_conference_files()
    all_conferences = []

    for file in files:
        data = download_yaml_file(file)
        if data:
            # Ensure it's a list (some files may have one conference as a dict)
            if isinstance(data, dict):
                data = [data]

            current_year = datetime.now().year  # Get the current year dynamically
            
            # Keep only conferences from the current year
            for conf in data:
                if "year" in conf and conf["year"] == current_year:
                    all_conferences.append(conf)

    # Save merged YAML file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        yaml.dump(all_conferences, f, default_flow_style=False, allow_unicode=True)

    print(f"✅ Merged {len(all_conferences)} conferences into {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_conferences()
