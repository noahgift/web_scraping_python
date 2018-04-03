import logging
import os
import csv
from io import StringIO

import boto3
from bs4 import BeautifulSoup
import requests
from chalice import (Chalice, Rate)
from slackclient import SlackClient

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
APP_NAME = 'scrape-yahoo' 
app = Chalice(app_name=APP_NAME)
app.log.setLevel(logging.DEBUG)

def create_s3_file(data, name="birthplaces.csv"):

    csv_buffer = StringIO()
    app.log.info(f"Creating file with {data} for name")
    writer = csv.writer(csv_buffer)
    for key, value in data.items():
        writer.writerow([key,value])
    s3 = boto3.resource('s3')
    res = s3.Bucket('aiwebscraping').\
        put_object(Key=name, Body=csv_buffer.getvalue())
    return res

def fetch_page(url="https://sports.yahoo.com/nba/stats/"):
    """Fetchs Yahoo URL"""

    #Download the page and convert it into a beautiful soup object
    app.log.info(f"Fetching urls from {url}")
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    return soup

def get_player_links(soup):
    """Gets links from player urls
        
   Finds urls in page via the 'a' tag and filter for nba/players in urls
    """
    
    nba_player_urls = []
    for link in soup.find_all('a'):
        link_url = link.get('href')
        #Discard "None"
        if link_url:
            if "nba/players" in link_url:
                print(link_url)
                nba_player_urls.append(link_url)
    return nba_player_urls

def fetch_player_urls():
    """Returns player urls"""

    soup = fetch_page()
    urls = get_player_links(soup)
    return urls


def find_birthplaces(urls):
    """Get the Birthplaces From Yahoo Profile NBA Pages"""

    birthplaces = {}
    for url in urls:
        profile = requests.get(url)
        profile_url = BeautifulSoup(profile.content, 'html.parser')
        lines = profile_url.text
        res2 = lines.split(",")
        key_line = []
        for line in res2:
            if "Birth" in line:
                #print(line)
                key_line.append(line)
        try:
            birth_place = key_line[0].split(":")[-1].strip()
            app.log.info(f"birth_place: {birth_place}")
        except IndexError:
            app.log.info(f"skipping {url}")
            continue
        birthplaces[url] = birth_place
        app.log.info(birth_place)
    return birthplaces

#These can be called via HTTP Requests
@app.route('/')
def index():
    """Root URL"""

    app.log.info(f"/ Route: for {APP_NAME}")
    return {'app_name': APP_NAME}

@app.route('/player_urls')
def player_urls():
    """Fetches player urls""" 

    app.log.info(f"/player_urls Route: for {APP_NAME}")
    urls = fetch_player_urls()
    return {"nba_player_urls": urls}

#This a standalone lambda
@app.lambda_function()
def return_player_urls(event, context):
    """Standalone lambda that returns player urls"""

    app.log.info(f"standalone lambda 'return_players_urls' {APP_NAME} with {event} and {context}")
    urls = fetch_player_urls()
    return {"urls": urls}

#This a standalone lambda 
@app.lambda_function()
def birthplace_from_urls(event, context):
    """Finds birthplaces"""

    app.log.info(f"standalone lambda 'birthplace_from_urls' {APP_NAME} with {event} and {context}")
    payload = event["urls"]
    birthplaces = find_birthplaces(payload)
    return birthplaces

#This a standalone lambda 
@app.lambda_function()
def create_s3_file_from_json(event, context):
    """Create an S3 file from json data"""

    app.log.info(f"Creating s3 file with event data {event} and context {context}")
    print(type(event))
    res = create_s3_file(data=event)
    app.log.info(f"response of putting file: {res}")
    return True

@app.lambda_function()
def send_message(event, context):
    """Send a message to a channel"""

    slack_client = SlackClient(SLACK_TOKEN)
    res = slack_client.api_call(
      "chat.postMessage",
      channel="#general",
      text=event
    )
    return res


#This is a timed lambda
@app.schedule(Rate(5, unit=Rate.MINUTES))
def timed_handler(event):
    """Timed handler that gets called every 5 minutes

    Useful for scheduling jobs
    """
    
    app.log.info(f"'timed_handler' called for {APP_NAME} with {event}")
    return True