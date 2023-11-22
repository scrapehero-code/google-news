import json
import base64
import csv

import requests
from lxml.html import fromstring


proxies = {
    # 'http': 'Provide your proxy here',
    # 'https': 'Provide your proxy here'
}

def decode_base64(encoded_url):
    """
    Function to decode base64 encoded string

    Args:
        encoded_url (str): encoded base64 string

    Returns:
        str: decoded string
    """
    # Decode the base64-encoded URL and convert it to a UTF-8 string
    decoded_string = base64.b64decode(encoded_url).decode("utf-8")

    
    # The line `return json.loads(decoded_string)[-1]` is decoding a JSON string and returning the
    # last element of the resulting list.
    return json.loads(decoded_string)[-1]


def extract_base64_string(url):
    """
    Function to extract a base64 string from url

    Args:
        url (str): article url which as encoded base64 string

    Returns:
        str: extracted encoded base64 string
    """
    # Split the URL by semicolon, then further split the second part by colon to extract the base64 string
    return url.split(";")[1].split(":")[1]


def fetch_html_response(search_keyword):
    params = {
        "q": search_keyword,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }
    headers = {
        "authority": "news.google.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-bitness": '"64"',
        "sec-ch-ua-full-version-list": '"Chromium";v="116.0.5845.179", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.179"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Linux"',
        "sec-ch-ua-platform-version": '"6.2.0"',
        "sec-ch-ua-wow64": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    }
    response = requests.get("https://news.google.com/search", params=params, headers=headers, proxies=proxies)
    return response


def write_to_csv(data_scraped):
    """
    Saving the required data points as csv file
    """
    csv_filename = "news_articles.csv"
    with open(csv_filename, "w", newline="") as file:
        fieldnames = data_scraped[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_scraped:
            writer.writerow(row)


def extract_data_from_html(response):
    """
    Function to extract required data points and returns the it

    Args:
        response (response): response object containing HTML response of the website

    Returns:
        list: required data points as list of dict
    """
    # Initialize an empty list to store extracted data
    data_scraped = []

    parser = fromstring(response.text)
    news_tags = parser.xpath('//div[@class="NiLAwe y6IFtc R7GTQ keNKEd j7vNaf nID9nc"]')
    for news_tag in news_tags:
        title = news_tag.xpath('.//h3[@class="ipQwMb ekueJc RD0gLb"]/a/text()')[0]
        time = news_tag.xpath('.//time[@class="WW6dff uQIVzc Sksgp slhocf"]/text()')[0]
        url = news_tag.xpath('.//a[@class="VDXfz"]/@jslog')[0]
        encoded_url = extract_base64_string(url)
        article_url = decode_base64(encoded_url)
        data = {
            "article_title": title,
            "time": time,
            "article_url": article_url,
        }
        data_scraped.append(data)
    return data_scraped


if __name__ == "__main__":
    # Define the search keyword for web scraping
    search_keyword = "Sports"

    # Send an HTTP request and get the HTML response
    response = fetch_html_response(search_keyword)
    
    # Checks response is valid
    if response.status_code == 200:
        # Extract data from the HTML and store it in 'data_scraped'
        data_scraped = extract_data_from_html(response)

        # Write the extracted data to a CSV file
        write_to_csv(data_scraped)
    else:
        print('Invalid Response')
