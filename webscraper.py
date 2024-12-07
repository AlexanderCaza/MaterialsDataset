
# The Web Scraper to obtain initial material data
# Copyright Alexander Caza and Spectre Defense
# Created: Dec 6, 2024

# Imports
# importing os module for environment variables
import os
from xml.etree.ElementTree import fromstring, tostring

# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
import requests;
from bs4 import BeautifulSoup

def get_webpage_contents(url):
    request = requests.get(url)
    contents = request.text
    return contents

def get_urls_from_container(html, url):
    urls = []
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find(class_="cards-container")
    children = container.find_all('a')
    for child in children:
        href = child['href']
        root = os.getenv("ROOT")
        print(href)
        if href.startswith('../', 0, 3):
            href = href.replace('..', root, 1)
            print(href)
            second_level_html = get_webpage_contents(href)
            try:
                second_level_hrefs = get_urls_from_container(second_level_html, url)
                urls.extend(second_level_hrefs)
            except:
                urls.append(href)
        elif href.startswith('./', 0, 3):
            href = href.replace('.', root, 1)
            urls.append(href)
    return urls

def main():
    # loading variables from .env file
    load_dotenv()
    root = os.getenv("ROOT")
    initial_url = root + os.getenv("STARTING_PATH")
    html = get_webpage_contents(initial_url)
    webpages_to_scrape = get_urls_from_container(html, initial_url)
    print(len(webpages_to_scrape))
    print(webpages_to_scrape)

if __name__ == "__main__":
    main()
