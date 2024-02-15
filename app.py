import os
import streamlit as st
from pathlib import Path
# from openai import AzureOpenAI
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *
# from langchain.schema import (
#     AIMessage,
#     HumanMessage,
#     SystemMessage
# )

# from langchain_community.callbacks import get_openai_callback

from html_template import css, bot_template, user_template

env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# Load env settings
env_file_path = Path(f"./.env.{env_name}")
print(f"Loading environment from: {env_file_path}")
with open(env_file_path) as f:
    dotenv.load_dotenv(dotenv_path=env_file_path)
# print(os.environ)

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


def main():

    st.set_page_config(page_title="RAG App Accelerator", page_icon=":books:")

    st.image("img/Cognitive-Search.svg", width=78)

    st.write(
        """
        # RAG App Accelerator

        Welcome! 👋 This accelerator shows various solutions I am working on to showcase the power of 
        Azure OpenAI and Cognitive Search to build RAG (Retrieval Augmented Generation) based solutions. 
        Each page is a demonstration of specific feature or capability of various patterns/approaches of LLM Apps.
        ✨
        """
    )

    st.info(
        """
        Need to include a tpoic or a capability that's not on here?
        [Let me know by opening a GitHub issue!](https://github.com/pieofcode/pdf-chat-app/issues)
        """,
        icon="👾",
    )

    st.write("\n\n")
    st.markdown("#### Reference Architecture")
    st.write(
        """
        This is a typical architecture of a RAG based app leveraging Azure Platform Services. 
        """
    )

    st.image("img/arch.png")


if __name__ == "__main__":
    main()
