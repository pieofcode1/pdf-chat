import os
import streamlit as st
from pathlib import Path
import dotenv
import pandas as pd
from framework.text_loader import *


def handle_user_input(question):
    print(f"Question: {question}")
    # Cosmos DB API
    response = st.session_state.ignite_cosmos_agent.vector_search("Products", "contentVector", question, limit=3)
    for item in response:
        col1, col2 = st.columns([5, 3])
        with col1:
            image_url = st.session_state.ignite_storage_agent.generate_blob_sas_token(item['document']['key'])
            st.image(image_url)
        with col2:
            st.write(f"Similarity Score: {item['similarityScore']}")
            st.write(f"Id: {str(item['document']['_id'])}")
            st.write(f"Name: {item['document']['name']}")
            st.write(f"Key: {item['document']['key']}")
 
        # st.image(image_url, caption=f"{item['product_name']}", use_column_width=True)
        st.write("--------------------------------------------------")

def main():

    st.set_page_config(page_title="Image Search Result", page_icon=":frame_with_picture:", layout="wide")

    if "image_data" not in st.session_state:
        st.session_state.image_data = None
        st.session_state.search_text = None

    # Initialize Session state
    if "ignite_cosmos_agent" not in st.session_state:
        st.session_state.ignite_cosmos_agent = None
        st.session_state.ignite_storage_agent = None

    st.header("Image Search :frame_with_picture:", divider='grey')
    if st.session_state.ignite_cosmos_agent is None:
        st.session_state.ignite_cosmos_agent = create_cosmos_vector_search_agent(container_names=["Products"], db="IgniteDB", embedding_agent_type="ai_vision")
        st.session_state.ignite_storage_agent = create_storage_agent(container_name="flyer-deals")

    
    with st.sidebar:
         
        tab_text, tab_img, = st.tabs(["Text", "Image"])

        with tab_text:
            
            st.session_state.search_text = st.text_input("Search Text", placeholder="Searching for images")
            st.write(f"Searching for: {st.session_state.search_text}")
            

        with tab_img:
            image_file = st.file_uploader(
                "Find Similar products ", accept_multiple_files=False)
            
            if image_file != None:

                # process the information from Imgage
                with st.spinner("Processing"):
                    # To read file as bytes:
                    image_data = image_file.getvalue()
                    st.session_state.image_data = image_data
                    st.image(st.session_state.image_data)

                    st.button("Search")

    # Handle user input and search the product images based on the text
    if st.session_state.search_text:
        handle_user_input(st.session_state.search_text)

if __name__ == "__main__":
    main()
