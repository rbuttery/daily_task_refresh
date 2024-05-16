import os
# from dotenv import load_dotenv
# load_dotenv()

import requests
import json

# # setup a log under notion.log
# import logging
# logging.basicConfig(filename="notion.log", level=logging.INFO)

# create a class to interact with the Notion API
class NotionClient:
    def __init__(self):
        # update the log
        # logging.info("Initializing NotionClient")
        self.token = os.getenv("NOTION_API_KEY")
        self.url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def search(self, query, page_or_database="database"):
        payload = {
            "query": query,
            "filter": {
                "value": page_or_database,
                "property": "object"
            }
        }
        response = requests.post(url=f"{self.url}/search", headers=self.headers, json=payload)
        if 'results' in response.json():
            return response.json()['results']
        else:
            return response.json()
        
    def get_database(self, database_id):
        response = requests.get(url=f"{self.url}/databases/{database_id}", headers=self.headers)
        return response.json()
    
    def get_database_rows(self, database_id):
        response = requests.post(url=f"{self.url}/databases/{database_id}/query", headers=self.headers)
        return response.json()
    
    def get_page(self, page_id):
        response = requests.get(url=f"{self.url}/pages/{page_id}", headers=self.headers)
        return response.json()
    
    def create_page(self, database_id, title, properties):
        payload = {
            "parent": {
                "database_id": database_id
            },
            "properties": properties
        }
        response = requests.post(url=f"{self.url}/pages", headers=self.headers, json=payload)
        return response.json()

