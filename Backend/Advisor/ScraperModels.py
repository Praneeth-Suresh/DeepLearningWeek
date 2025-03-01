# Get the scraper

from urllib.request import urlopen
from urllib.parse import urlparse

import pickle

from bs4 import BeautifulSoup

refresh = False

# Get the Google LLM client set up
from google import genai
from pydantic import BaseModel
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import os

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

Gclient = genai.Client(api_key=GEMINI_API_KEY)

# Get the cloudfare API set up

import requests

CLOUDFARE_API_TOKEN = "jgCBig6iRJdHEwt1yXJQwdrYfRKLGZoU6uDHEIta"
# CLOUDFARE_API_TOKEN = os.environ["CLOUDFARE_API_TOKEN"]

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/7334438e0dd62f7a7d9989ba0b0b6ee5/ai/run/"
headers = {"Authorization": f"Bearer {CLOUDFARE_API_TOKEN}"}

def run(model, inputs):
    input = { "messages": inputs }
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()

def GetInstaPost(url): # The goal of this function is to retrieve the text in the social media page linked to url

    page = urlopen(url)

    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    title_index = html.find("<title")

    i = 0

    while True:
        i += 1 
        if html[title_index + i] == ">":
            start_index = title_index + i + 1
            break

    end_index = html.find("</title>")
    title = html[start_index:end_index]

    print(title)

    soup = BeautifulSoup(html, "html.parser")

    # Extract post text from the meta tag
    meta_tag = soup.find("meta", property="og:description")
    if meta_tag:
        return meta_tag["content"]
    else:
        return "Error: Could not find post text."
    

# insta_url = "https://www.instagram.com/p/DGloshmMmnt/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=="
# print(GetInstaPost(insta_url))