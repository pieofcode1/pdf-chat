import os
import streamlit as st
from pathlib import Path
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *


def main():

    st.set_page_config(page_title="ClipCognition Video RAG", page_icon=":movie_camera:", layout="wide")

    # Initialize Session state
    if "search_agent" not in st.session_state:
        st.session_state.search_agent = None
        st.session_state.search_agent = create_bing_search_agent()

    st.header("ClipCognition Video Search :movie_camera:", divider='grey')
    st.session_state.search_agent = create_bing_search_agent()

    messages = st.container()
    if prompt := st.chat_input("Search text"):
        response = st.session_state.search_agent.results(prompt, 3)
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(f"{response}")
    

if __name__ == "__main__":
    main()
