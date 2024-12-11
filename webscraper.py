
# The Web Scraper to obtain initial material data
# Copyright Alexander Caza and Spectre Defense
# Created: Dec 6, 2024

# Imports
# Importing os module for environment variables
import os
from types import NoneType

# Importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values
from bs4 import BeautifulSoup

# importing requests to handle making HTTP GET requests
import requests

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


def get_header(header_intermediate):
    header = None
    try:
        header = header_intermediate.button.contents[0]
        if (header == None):
            raise Exception("No Contents")
    except:
        # Regular header
        try:
            header = header_intermediate.string
            if (header == None):
                raise Exception("No Contents")
        # Multi-section table header
        except:
            # header with button
            string_candidates = header_intermediate.descendants
            string_assembled = ""
            for string_candidate in string_candidates:
                if type(string_candidate) == type(BeautifulSoup("<b>e</b>", 'html.parser').b.string):
                    string_assembled += string_candidate
            header = string_assembled
    finally:
        if header != "\n":
            return header


def save_data(container, file_name):
    write_file = open(file_name, 'a+')
    table_body = container.find("tbody")
    rows = table_body.find_all("tr")
    # Whether file has subheadings embedded as "tr"s
    cleanup_needed = False
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 1:
            cleanup_needed = True
        for cell in cells:
            cell_data = cell.string
            if (type(cell_data) == NoneType):
                cell_data = ""
            write_file.write(cell_data + ",")
        write_file.write("\n")
    if cleanup_needed:
        # Cleaning up tables with subheadings embedded as "tr"s
        # Returning to start of file
        write_file.flush()
        read_file = open(file_name, 'r')
        new_lines = []
        # Reading first line and adding additional info header
        header = read_file.readline()
        new_header = header.replace("\n", "Additional_Info,\n")
        # Adding new header
        new_lines.append(new_header)
        # Going through data rows and shifting subheaders to Additional Info column
        subheader = ",\n"
        for line in read_file.readlines():
            if line.count(',') < 2:
                subheader = line
            else:
                new_line = line.replace("\n", subheader)
                new_lines.append(new_line)
        # Rewrite file
        read_file.close()
        # Returning to start to rewrite original file
        write_file = open(file_name, 'w')
        for line in new_lines:
            write_file.write(line)
    write_file.close()



def save_table(url):
    html = get_webpage_contents(url)
    soup = BeautifulSoup(html, "html.parser")
    containers = soup.find_all("table")
    # In case there's multiple discrete tables on the same page
    for container in containers:
        # Creating file
        table_name = container.find("caption").string.replace(' ', '_')
        file_name = "./tables/" + table_name + ".csv"
        file = open(file_name, 'w')
        # Saving headers
        headers_intermediate = container.find_all("th")
        for header_intermediate in headers_intermediate:
            header = get_header(header_intermediate)
            file.write(header.strip() + ",")
        file.write("\n")
        file.close()
        # Saving table data
        save_data(container, file_name)

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
