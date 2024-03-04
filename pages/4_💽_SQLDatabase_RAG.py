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
        # st.session_state.query_agent = create_sql_agent_executor(executor_type="db_chain")

    st.header("Chat with your Database :minidisc:", divider='blue')
    st.session_state.sql_agent = create_sql_agent_executor(executor_type="db_chain")

    messages = st.container()
    if prompt := st.chat_input("Say something"):
        response = st.session_state.sql_agent.invoke({"input": prompt})
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(f"{response}")

    with st.sidebar:
        st.header(":blue[Current Database]")
        selected_db_server = st.selectbox(
            'Choose endpoint',
            [os.environ["SQL_SERVER_ENDPOINT"]]
        )

        selected_db = st.selectbox(
            'Choose database',
            [os.environ["SQL_SERVER_DATABASE"]]
        )


if __name__ == "__main__":
    main()
