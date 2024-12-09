
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
        if href.startswith('../..', 0, 3):
            href = href.replace('../..', root, 1)
            urls.append(href)
        elif href.startswith('../', 0, 3):
            href = href.replace('..', root, 1)
            urls.append(href)
        elif href.startswith('./', 0, 3):
            href = href.replace('.', root, 1)
            second_level_html = get_webpage_contents(href)
            try:
                second_level_hrefs = get_urls_from_container(second_level_html, url)
                urls.extend(second_level_hrefs)
            except:
                urls.append(href)
    return urls


def save_table(url):
    html = get_webpage_contents(url)
    soup = BeautifulSoup(html, "html.parser")
    containers = soup.find_all("table")
    for container in containers:
        table_name = container.find("caption").string.replace(' ', '_')
        file = open("./tables/" + table_name + ".csv", 'w')
        headers_intermediate = container.find_all("th")
        for header_intermediate in headers_intermediate:
            try:
                header = header_intermediate.button.contents[0]
                if (header == None):
                    raise Exception("No Contents")
            except:
                try:
                    header = header_intermediate.string
                    if (header == None):
                        raise Exception("No Contents")
                except:
                    string_candidates = header_intermediate.descendants
                    string_assembled = ""
                    for string_candidate in string_candidates:
                        if type(string_candidate) == type(BeautifulSoup("<b>e</b>").b.string, 'html.parser'):
                            string_assembled += string_candidate
                            print(True)
                    header = string_assembled
                    print(table_name)
                    print(header)
            file.write(header.strip() + ",")


def download_tables(urls):
    for url in urls:
        save_table(url)


def main():
    # loading variables from .env file
    load_dotenv()
    # Getting all webapges with tables to scrape
    root = os.getenv("ROOT")
    initial_url = root + os.getenv("STARTING_PATH")
    html = get_webpage_contents(initial_url)
    urls_to_scrape = get_urls_from_container(html, initial_url)
    download_tables(urls_to_scrape)


if __name__ == "__main__":
    main()
