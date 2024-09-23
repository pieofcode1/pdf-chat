import os
import base64
import streamlit as st
from io import StringIO
from pathlib import Path
from openai import AzureOpenAI
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain_community.callbacks import get_openai_callback

from html_template import css, bot_template, user_template

# env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# # Load env settings
# env_file_path = Path(f"./.env.{env_name}")
# print(f"Loading environment from: {env_file_path}")
# with open(env_file_path) as f:
#     dotenv.load_dotenv(dotenv_path=env_file_path)
# # print(os.environ)

# openai.api_type: str = "azure"
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
# model: str = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")

# openai_client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
# )


def handle_user_input(question):
    if not st.session_state.image_data:
        st.write("Please upload an image.")
        return

    response = gpt4v_completion(
        st.session_state.image_data, question=question)

    print(response)
    st.session_state.chat_history.append({
        'question': question,
        'answer': response.choices[0].message.content
    })
    # st.write(response)
    # print(f"Chat History Type: {type(st.session_state.chat_history)}")
    # for i, message in enumerate(reversed(st.session_state.chat_history)):
    for i, message in enumerate(st.session_state.chat_history):
        print(F"Idx: {i}, Message: {message}")

        with st.chat_message("user"):
            st.write(message['question'])

        with st.chat_message("assistant"):
            st.write(message['answer'])


def main():

    st.set_page_config(page_title="Image Analysis",
                       page_icon=":page_with_curl:", layout="wide")
    st.write(css, unsafe_allow_html=True)

    # Initialize Session state
    if "image_data" not in st.session_state:
        st.session_state.image_data = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = list()

    st.header("Extract Insights from the doc :page_with_curl:", divider='blue')

    # user_question = st.text_input("Ask a question about your documents")
    user_question = st.chat_input("Ask a question about the image")
    if user_question:
        handle_user_input(user_question)

    with st.sidebar:
        st.subheader("Choose your Image")
        image_file = st.file_uploader(
            "Upload an image to start q & a", accept_multiple_files=False)

        if image_file != None:

            # process the information from PDFs
            with st.spinner("Processing"):

                # Step 1: Get raw contents from PDFs
                # To read file as bytes:
                image_data = image_file.getvalue()
                if image_data != st.session_state.image_data:
                    st.session_state.chat_history = list()

                # st.write(image_data)
                st.session_state.image_data = image_data
                st.image(st.session_state.image_data)


if __name__ == "__main__":
    main()
