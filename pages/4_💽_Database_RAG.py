import os
import streamlit as st
from pathlib import Path
import dotenv
from framework.text_loader import *
from framework.az_ai_search_helper import *


env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# Load env settings
env_file_path = Path(f"./.env.{env_name}")
print(f"Loading environment from: {env_file_path}")
with open(env_file_path) as f:
    dotenv.load_dotenv(dotenv_path=env_file_path)
# print(os.environ)


def main():

    st.set_page_config(page_title="Search Database", page_icon=":minidisc:")

    # Initialize Session state
    # if "sql_agent" not in st.session_state:
    #     st.session_state.sql_agent = None
    #     st.session_state.sql_agent = create_sql_agent_executor()

    if "query_agent" not in st.session_state:
        st.session_state.query_agent = None
    if "source_engine" not in st.session_state:
        st.session_state.source_engine = "SQL Database"
        # st.session_state.query_agent = create_sql_agent_executor(executor_type="db_chain")

    st.header(f"Chat with your {st.session_state.source_engine} :minidisc:", divider='blue')
    # st.session_state.sql_agent = create_sql_agent_executor(executor_type="db_chain", source=st.session_state.source_engine or "sqldb")

    messages = st.container()
    if prompt := st.chat_input("Ask your question"):
        response = st.session_state.sql_agent.invoke({"input": prompt})
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(f"{response['output']}")

    with st.sidebar:
        
        with st.expander(":blue[SQL Database]"):
            print("Active Tab: SQL")
            selected_db_server = st.selectbox(
                'Choose endpoint',
                [os.environ["SQL_SERVER_ENDPOINT"]]
            )

            selected_db = st.selectbox(
                'Choose database',
                [os.environ["SQL_SERVER_DATABASE"]]
            )
            st.session_state.source_engine = "SQL Database"

            # Connect to the selected database
            if st.button(":blue[Connect to SQL]", type="secondary"):
                with st.spinner("Processing"):
                    print(f"Connecting to SQL Server")
                    st.session_state.sql_agent = create_sql_agent_executor(executor_type="db_chain", source="sqldb")

        with st.expander(":red[Databricks]"):
            print("Active Tab: Databricks")
            selected_db_catalog = st.selectbox(
                'Choose Catalog',
                [os.environ["DATABRICKS_CATALOG"]]
            )

            selected_db = st.selectbox(
                'Choose Schema',
                [os.environ["DATABRICKS_SCHEMA"]]
            )
            st.session_state.source_engine = "Databricks"
        
            # Connect to the selected database
            if st.button(":blue[Connect to Databricks]", type="primary"):
                with st.spinner("Processing"):
                    print(f"Connecting to {st.session_state.source_engine}")
                    st.session_state.sql_agent = create_sql_agent_executor(executor_type="db_chain", source="databricks")


if __name__ == "__main__":
    main()
