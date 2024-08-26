import os
import streamlit as st
from pathlib import Path
import dotenv
import pandas as pd
from framework.text_loader import *


def main():

    st.set_page_config(page_title="ClipCognition Video RAG", page_icon=":movie_camera:", layout="wide")

    # Initialize Session state
    if "search_agent" not in st.session_state:
        st.session_state.search_agent = None
        st.session_state.storage_agent = None
        st.session_state.index_client = None

    st.header("ClipCognition Video Search :movie_camera:", divider='grey')
    if st.session_state.search_agent is None:
        st.session_state.search_agent = create_cosmos_vector_search_agent(container_names=["CC_VideoAssets", "CC_VideoAssetFrames"])
        st.session_state.storage_agent = create_storage_agent()
        st.session_state.index_client = get_ai_search_index_client("cc-video-asset-frames-index")

    messages = st.container()
    if prompt := st.chat_input("Search text"):
        # Create embeddings for the prompt
        print(f"Prompt: {prompt}")
        query = generate_embeddings(prompt)
        # response = st.session_state.search_agent.search_vector_similarity("CC_VideoAssetFrames", query, top=1)
        response = perform_vector_search(
                            st.session_state.index_client, 
                            index_name="cc-video-asset-frames-index", 
                            vectorized_query=query, 
                            projection=["asset_name", "summary", "frame_id"] 
            )
        messages.chat_message("user").write(prompt)
        with messages.chat_message("assistant"):
            asset_name = response[0]['asset_name']
            ops_info, asset_info = st.session_state.search_agent.query_items("CC_VideoAssets", f"asset_name = '{asset_name}'")
            # Get the video url
            video_sas_url = st.session_state.storage_agent.generate_blob_sas_token(asset_info[0]['blob_video_key'])

            asset_info = asset_info[0]
            keys_to_remove = ['_rid', '_self', '_etag', '_attachments', '_ts', 'video_summary_vector', 'video_summary',  'audio_summary_vector', 'audio_summary', 'audio_transcription']
            asset_info = {k: v for k, v in asset_info.items() if k not in keys_to_remove}
            col1, col2 = st.columns([5, 3])
            with col1:
                st.video(video_sas_url)

            with col2:
                key_value_pairs = [(k, v) for k, v in asset_info.items()]
                df = pd.DataFrame(key_value_pairs)
                st.table(df)


if __name__ == "__main__":
    main()
