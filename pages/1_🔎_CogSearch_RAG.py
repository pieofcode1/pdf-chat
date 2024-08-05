import os
import streamlit as st
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


def handle_user_input(question):
    with get_openai_callback() as cb:
        if not st.session_state.has_vectorized_data:
            st.write(
                "Please upload your documents and hit Process to build vector store.")
            return

        response = st.session_state.conversation.invoke({"question": question})
        st.session_state.chat_history = response['chat_history']
        # st.write(response)
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

    st.set_page_config(page_title="PDF Chatbot",
                       page_icon=":books:", layout="wide")
    st.write(css, unsafe_allow_html=True)

    # Initialize Session state
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    if "has_vectorized_data" not in st.session_state:
        st.session_state.has_vectorized_data = None

    if "use_az_search_vector_store" not in st.session_state:
        st.session_state.use_az_search_vector_store = None

    if "selected_index" not in st.session_state:
        st.session_state.selected_index = None

    st.header("Chat with your Data (Cognitive Search) :books:", divider='blue')
    # user_question = st.text_input("Ask a question about your documents")
    user_question = st.chat_input("Ask a question about your documents")
    if user_question:
        print(f"User Question: {user_question}")
        handle_user_input(user_question)

    # st.write(bot_template.replace(
    #     "{{MSG}}", "Hello Human!"), unsafe_allow_html=True)
    # st.write(user_template.replace(
    #     "{{MSG}}", "Hello Bot!"), unsafe_allow_html=True)
    # with st.chat_message("user"):
    #     st.write("Hello assistant! 👋")
    # with st.chat_message("assistant"):
    #     st.write("Hello human! 👋")

    with st.sidebar:
        st.markdown("#### Cognitive Search Vector Store")
        st.write(
            """                 Cognitive Search Indexes are populated with the domain specific knowledgebase.""")
        st.write("\n\n")

        st.session_state.use_az_search_vector_store = True
        indices = get_az_search_indices()
        selected_index = st.selectbox(
            'Choose Vector Index to use',
            indices
        )
        st.write('You selected:', selected_index)

        if (selected_index != st.session_state.selected_index):
            st.session_state.chat_history = None
            st.session_state.selected_index = selected_index
            with st.spinner("Processing"):

                # Step 3: Create embeddings and store in Vector store
                vector_store = get_az_search_vector_store(selected_index)

                # Step 4: Get conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vector_store=vector_store)
                st.session_state.has_vectorized_data = True

        # add_sidebar = st.sidebar.selectbox(
        #     "EDSP Data Science", ('Data Engineering', 'Model Training'))


if __name__ == "__main__":
    main()
