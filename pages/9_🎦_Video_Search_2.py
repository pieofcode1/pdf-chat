import os
import streamlit as st
from pathlib import Path
import dotenv
import pandas as pd
from framework.text_loader import *
from framework.schema import *
from framework.class_definitions import *


@st.cache_resource
def create_ignite_search_agent(vector_store_type: str):
    return VectorSearchAgentFactory.create_vector_search_agent(vector_store_type=vector_store_type)

@st.cache_resource
def create_ignite_storage_agent():
    return create_storage_agent()

def perform_vector_search(prompt, limit=1):

    projection=["asset_name", "summary", "frame_id"]

    response = st.session_state.search_agent.perform_vector_search("CC_VideoAssetFrames", query=prompt, attr_name="summary_vector", projection=projection, limit=limit)  
    # print(response)

    # if st.session_state.vector_store == VectorStoreType.CosmosNoSQL.value:
    #     print("Searching in Cosmos DB NoSQL")
    #     prompt_vector = generate_embeddings(prompt)
    #     response = st.session_state.search_agent.perform_vector_search(
    #         "CC_VideoAssetFrames", prompt_vector, 
    #         content_vector_field="summary_vector", projection=projection , limit=limit)

    # elif st.session_state.vector_store == VectorStoreType.CosmosMongoVCore.value:
    #     print("Searching in Cosmos DB Mongo VCore")
    #     response = st.session_state.search_agent.perform_vector_search("CC_VideoAssetFrames", "summary_vector", prompt, limit=limit)

    # elif st.session_state.vector_store == VectorStoreType.AISearch.value:
    #     print("Searching in AI Search")
    #     response = perform_vector_search(
    #                         st.session_state.index_client, 
    #                         index_name="cc-video-asset-frames-index", 
    #                         vectorized_query=prompt, 
    #                         projection=projection 
    #         )
        
    # else:
    #     raise ValueError(f"Invalid vector store type: {st.session_state.vector_store}")

    return response

def main():

    st.set_page_config(page_title="ClipCognition Video RAG", page_icon=":cinema:", layout="wide")

    # Initialize Session state
    if "search_agent" not in st.session_state:
        st.session_state.search_agent = None
        st.session_state.index_client = None
        st.session_state.storage_agent = create_ignite_storage_agent()

    
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None


    # st.header("ClipCognition Video Search :movie_camera:", divider='grey')
    st.header(":blue[Clip Cognition] :cinema:")
    st.markdown("##### Searching video content")

    # Sidebar configuration
    with st.sidebar:    
        st.session_state.vector_store = st.selectbox(
            ":blue[Vector Store]",
            options=[vector_store_type.value for vector_store_type in VectorStoreType]
        )
        print(f"Selected Vector Store: {st.session_state.vector_store}")
        st.session_state.search_agent = create_ignite_search_agent(vector_store_type=st.session_state.vector_store)

    # if st.session_state.search_agent is None:
        # st.session_state.search_agent = VectorSearchAgentFactory.create_vector_search_agent(vector_store_type=st.session_state.vector_store)


    messages = st.container()
    if prompt := st.chat_input("Search text"):
        # Create embeddings for the prompt
        print(f"Prompt: {prompt}")
        # query = generate_embeddings(prompt)
        response = perform_vector_search(prompt, limit=1)
        # print(response)
        # with open("./results.json", "w") as f:
        #     f.write(json.dumps(response))
        messages.chat_message("user").write(prompt)
        if len(response) == 0:
            messages.chat_message("assistant").write("No results found.")
        else:
            with messages.chat_message("assistant"):
                asset_name = response[0]['asset_name']
                asset_info = st.session_state.search_agent.perform_search("CC_VideoAssets", filter={"asset_name": asset_name}, limit=1)
                print(asset_info)
                # Get the video url
                video_sas_url = st.session_state.storage_agent.generate_blob_sas_token(asset_info[0]['blob_video_key'])
                print(f"Asset URL: {video_sas_url}")
                asset_info = asset_info[0]
                keys_to_remove = ['_id', '_rid', '_self', '_etag', '_attachments', '_ts', 'video_summary_vector', 'video_summary',  'audio_summary_vector', 'audio_summary', 'audio_transcription']
                asset_info = {k: v for k, v in asset_info.items() if k not in keys_to_remove}
                col1, col2 = st.columns([5, 3])
                with col1:
                    st.video(video_sas_url)
                    # st.markdown(video_sas_url)

                with col2:
                    key_value_pairs = [(k, v) for k, v in asset_info.items()]
                    df = pd.DataFrame(key_value_pairs)
                    st.table(df)


if __name__ == "__main__":
    main()
