import os
import streamlit as st
from pathlib import Path
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *


# env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# # Load env settings
# env_file_path = Path(f"./.env.{env_name}")
# print(f"Loading environment from: {env_file_path}")
# with open(env_file_path) as f:
#     dotenv.load_dotenv(dotenv_path=env_file_path)
# # print(os.environ)


def main():

    st.set_page_config(page_title="Bing Web Search", page_icon=":books:")

    # Initialize Session state
    if "search_agent" not in st.session_state:
        st.session_state.search_agent = None
        st.session_state.search_agent = create_bing_search_agent()

    st.header("Bing Web Search :globe_with_meridians:", divider='grey')
    st.session_state.search_agent = create_bing_search_agent()

    messages = st.container()
    if prompt := st.chat_input("Say something"):
        response = st.session_state.search_agent.results(prompt, 3)
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(f"{response}")
    

if __name__ == "__main__":
    main()
