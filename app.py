import streamlit as st
import os

# from dotenv import load_dotenv
# load_dotenv()

from notion_client import NotionClient  
from google_client import GoogleClient



# @st.cache_data()
# def list_notion_tasks_by_google_task_id():
#         # Query the notion "Items" database
#         notion_items = NotionClient().get_database_rows(os.getenv("NOTION_DATABASE_ID"))['results']
        
#         def try_task_id(task):
#             try:
#                 return task['properties']['Task ID']['rich_text'][0]['text']['content']
#             except:
#                 return None

#         # This list contains unique task ids from the Notion Items database
#         return list(set([i for i in [try_task_id(x) for x in notion_items] if i != None]))
    

# def push_google_tasks_to_notion():
#     current_notion_ids = list_notion_tasks_by_google_task_id()
#     for task in GoogleClient().list_tasks():
        
#         # if the google task id is already in notion, skip it
#         if task['id'] in current_notion_ids:
#             # logging.info(f"Task {task['id']} already exists in Notion")
#             continue
        
#         # if google task does not have a title skip it
#         if task['title'] == '':
#             # logging.info(f"Task {task['id']} does not have a title")
#             continue
            
#         else:
#             icon = {'type': 'external',
#                     'external': {'url': 'https://www.notion.so/icons/square_green.svg'}}
            
#             props = {
#                 "Item": {
#                     "title": [
#                         {
#                             "text": {
#                                 "content": task['title']
#                             }
#                         }
#                     ]
#                 },
#                 "Done": {
#                     "checkbox": False if task['status'] == "needsAction" else True
#                 },
#                 "Task ID": {
#                     "rich_text": [
#                         {
#                             "text": {
#                                 "content": task['id']
#                             }
#                         }
#                     ]
#                 }
#             }
            
#             try:
#                 props['Due'] = {
#                         'type': 'date',
#                         'date': {
#                             'start': task['due'].replace('Z', '') if task['due'] else None,
#                             'end': None,
#                             'time_zone': None
#                         }
#                     }
#             except KeyError:
#                 pass
            
#             db_id = os.getenv("NOTION_DATABASE_ID")
#             new_page = NotionClient().create_page(database_id=db_id, properties=props, icon=icon)
#             # logging.info(f"Created task {task['id']} in Notion")
        
st.title("Google Tasks to Notion")

def test():
    st.write("Hello World")

st.button("Push Google Tasks to Notion", on_click=test)