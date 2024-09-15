import os
import streamlit as st
from pathlib import Path
from openai import AzureOpenAI
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *
from framework.llm_chain_agent import LLMChainAgent

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


def handle_user_input(question):
    with get_openai_callback() as cb:

        response = st.session_state.conversation.invoke(question)
        print(response)
        st.session_state.chat_history = response['history'] if response['history'] != "" else []
        st.session_state.chat_history.append(HumanMessage(question))
        st.session_state.chat_history.append(AIMessage(response['response']))
        
        # print(f"Chat History Type: {type(st.session_state.chat_history)}")
        # for i, message in enumerate(reversed(st.session_state.chat_history)):
        for i, message in enumerate(st.session_state.chat_history):
            print(F"Idx: {i}, Message: {message}")
            if type(message) == HumanMessage:
                # st.write(user_template.replace(
                #     "{{MSG}}", message.content), unsafe_allow_html=True)
                with st.chat_message("user"):
                    st.write(message.content)

            elif type(message) == AIMessage:
                # st.write(bot_template.replace(
                #     "{{MSG}}", message.content), unsafe_allow_html=True)
                with st.chat_message("assistant"):
                    st.write(message.content)

            else:
                st.write(
                    f"Error displaying message of Type[{type(message)}], Content[{message.content}]")

        print(cb)


def main():

    st.set_page_config(page_title="PDF Chatbot", page_icon=":books:", layout="wide")
    st.write(css, unsafe_allow_html=True)

    # Initialize Session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    st.header("Chat with LLM :books:", divider='red')
    # user_question = st.text_input("Ask a question about your documents")

    if st.session_state.conversation is None:
        # Get the conversation Chain
        st.session_state.conversation = LLMChainAgent.get_llm_chain_with_history()

    user_question = st.chat_input("Ask a question about your documents")
    if user_question:
        handle_user_input(user_question)

    
if __name__ == "__main__":
    main()
