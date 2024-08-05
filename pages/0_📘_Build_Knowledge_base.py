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

    st.set_page_config(page_title="Bing Search", page_icon=":books:")

    # Initialize Session state
    if "index_name" not in st.session_state:
        st.session_state.index_name = None
    if "user_question" not in st.session_state:
        st.session_state.user_question = None
    if "has_vectorized_data" not in st.session_state:
        st.session_state.has_vectorized_data = None

    st.header("Build your knowledgebase :books:", divider='green')

    index_name = st.text_input(
        'Cognitive Search Index name', placeholder='Name of the index')
    if index_name:
        st.session_state.index_name = index_name

    pdf_docs = st.file_uploader(
        "Upload your PDFs here and click on 'Process' ", accept_multiple_files=True)

    if st.button(":blue[Create Index]", type="secondary"):
        if len(pdf_docs) != 0:
            # process the information from PDFs
            with st.spinner("Processing"):
                # Step 1: Create Azure Cognitive Search Index
                # Step 2: Upload PDFs to Azure Cognitive Search Index
                create_cogsearch_index(st.session_state.index_name, embeddings)
                upload_docs_to_cogsearch_index(
                    st.session_state.index_name, pdf_docs)
                st.success("Index created successfully")
        else:
            st.write("Please upload PDF documents")

    with st.sidebar:
        st.header(":blue[Cognitive Search indices]")
        index_names = get_az_search_indices()
        for index_name in index_names:
            st.write(index_name)


if __name__ == "__main__":
    main()
