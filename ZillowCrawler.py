import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import csv
import os
import re


num_pages = int(input("Enter the number of pages to iterate: "))

keywords = []
with open('Keywords.csv', mode='r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        keywords.extend([keyword.strip().lower() for keyword in row])
print(f"Keywords loaded: {keywords}")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5',
}
def extract_links(page_number):
    url = f"https://www.zillow.com/me/{page_number}_p/"
    print(f"Fetching URL: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(f"Successfully fetched page {page_number}")
    else:
        print(f"Failed to fetch page {page_number} with status code {response.status_code}")
        return set()
    soup = BeautifulSoup(response.content, 'html.parser')
    zpid_links = set(re.findall(r'(\d+_zpid)', str(soup)))
    print(f"Found {len(zpid_links)} unique zpid links on page {page_number}")
    return zpid_links
def page_contains_keywords(url, keywords, threshold=80):
    print(f"Checking link: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch link {url} with status code {response.status_code}")
        return False
    soup = BeautifulSoup(response.content, 'html.parser')
    text_elements = soup.find_all(class_=re.compile(r'^Text-c11n'))
    page_content = ' '.join(element.get_text() for element in text_elements).lower()
    for keyword in keywords:
        if keyword in page_content:
            print(f"Exact match for '{keyword}' found in the page content.")
            return True
    for keyword in keywords:
        ratio = fuzz.partial_ratio(keyword, page_content)
        if ratio >= threshold:
            print(f"Fuzzy match for '{keyword}' found in the page content with ratio {ratio}.")
            return True
    print(f"No keywords found in {url}")
    return False
output_file = 'SF_Accepted.txt'
if os.path.exists(output_file):
    os.remove(output_file)
processed_links = set()
for page_number in range(1, num_pages + 1):
    zpids = extract_links(page_number)
    for zpid in zpids:
        link = f"https://www.zillow.com/homedetails/{zpid}"
        if link not in processed_links:
            processed_links.add(link)
            if page_contains_keywords(link, keywords):
                with open(output_file, mode='a') as file:
                    file.write(link + '\n')
                print(f"Link saved: {link}")
        else:
            print(f"Duplicate link skipped: {link}")
print("Web crawling complete. Relevant links have been saved to SF_Accepted.txt.")
