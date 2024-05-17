import streamlit as st
import os
import requests

# Get the environment variable
api_url = 'https://tg7js80g-5000.use.devtunnels.ms'
# api_url = 'http://127.0.0.1:5000'

col1, col2, col3 = st.columns(3)

with col1:
    # create a button for each endpoint:
    if st.button('Push to Google Tasks', use_container_width=True):
        
        with st.spinner('Pushing tasks to Google Tasks...'):
            requests.get(api_url + '/push_to_google_tasks')
            st.success('Pushed tasks to Google Tasks!')
            st.balloons()
with col2:
    if st.button('Update Google Tasks', use_container_width=True):
        with st.spinner('Updating Google Tasks...'):
            requests.get(api_url + '/update_google_tasks')
            st.balloons()
            st.success('Updated Google Tasks!')
with col3:     
    if st.button('Push to Notion', use_container_width=True):
        with st.spinner('Pushing tasks to Notion...'):
            requests.get(api_url + '/push_to_notion')
            st.success('Pushed tasks to Notion!')
            st.balloons()
    
if st.button('Sync All', use_container_width=True):
    with st.spinner('Syncing all tasks...'):    
        requests.get(api_url + '/sync_all')
        st.success('Synced all tasks!')    
        st.balloons()    