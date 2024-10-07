import argparse
from bs4 import BeautifulSoup
import re
import fileinput
import requests
import json
import time
from pygments import highlight, lexers, formatters

# Lists for exclusion filters
exclude_type = [
    "text/kendo-template"
]

exclude_ext = [
    ".jpg",
    ".png",
    ".css",
    ".map",
    ".pdf"
]

exclude_file = [
    "jquery",
    "moment",
    "bootstrap",
    "chart",
    "gauge"
]

#TODO choise for user agent
user_agent = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"}

# Global variables to hold results and cookies
results = {}
cookies = {}
seconds = 0

# Setup argparse
parser = argparse.ArgumentParser(description="Process URLs from a file and extract JavaScript functions.")

parser.add_argument("-i", "--input", required=True, help="Path to the input file containing URLs.")
parser.add_argument("-c", "--cookie", help="Cookie string in 'key=value' format. Separate multiple cookies with ';'.")
parser.add_argument("-s", "--seconds", type=int, default=0, help="Time to wait in seconds between requests.")

# Parse the arguments
args = parser.parse_args()

seconds = args.seconds 

# Handle cookies if provided
if args.cookie:
    pairs = args.cookie.strip().split(';')
    for pair in pairs:
        # Ensure the cookie pair has both a key and a value
        if '=' in pair:
            key, value = pair.split('=', 1)
            cookies[key] = value
        else:
            print(f"Invalid cookie format: {pair}")
            continue

# Regular expression to match JavaScript function definitions
# pattern = r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)"
pattern = r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)"

# Read URLs from the input file
for url in fileinput.input(files=args.input):
    time.sleep(seconds)
    url = url.strip()

    # Skip excluded URLs based on file extensions or keywords
    if any(ext in url.lower() for ext in exclude_ext) or any(f in url.lower() for f in exclude_file):
        continue

    # If the URL ends with .js, get JavaScript functions directly from the content
    if url.endswith(".js"):
        results[url] = [x for x in re.findall(pattern, requests.get(url, cookies=cookies, headers=user_agent).text)]

    # For other URLs, parse the HTML to find <script> tags
    result = requests.get(url, cookies=cookies, headers=user_agent)
    soup = BeautifulSoup(result.text, 'html.parser')
    for script in soup.find_all('script'):
        if not script.get("src") and script.get("type") not in exclude_type:
            if url not in results:
                results[url] = []
            results[url].extend([x for x in re.findall(pattern, script.text)])

# Print the results with syntax highlighting
print(highlight(json.dumps(results, ensure_ascii=False, indent=1), lexers.JsonLexer(), formatters.TerminalFormatter()))
