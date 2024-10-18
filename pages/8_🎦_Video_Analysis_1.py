import os
import streamlit as st
from pathlib import Path
from PIL import Image
from io import BytesIO
import dotenv
from framework.text_loader import *
from framework.video_processor import VideoProcessingAgent
from framework.schema import *


# env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# # Load env settings
# env_file_path = Path(f"./.env.{env_name}")
# print(f"Loading environment from: {env_file_path}")
# with open(env_file_path) as f:
#     dotenv.load_dotenv(dotenv_path=env_file_path)
# # print(os.environ)


def show_details():
    if st.session_state.agent is not None and st.session_state.agent.is_complete == True:

        col_1, col_2 = st.columns([3, 1])

        with col_1:
            st.subheader(f"{st.session_state.agent.video_file_name}")
            st.write(":blue[Asset URLs]")
            st.write(f"{st.session_state.agent.blob_url_video}")
            st.write(f"{st.session_state.agent.blob_url_audio}")
        
        with col_2:
            st.write(":blue[Size]")
            st.subheader(f"{len(st.session_state.agent.video_data)}")
            
            st.write(":blue[Duration]")
            st.subheader(f"{len(st.session_state.agent.video_frames) * st.session_state.agent.fps}")
            
            st.write(":blue[Frame Offset]")
            st.subheader(f"{st.session_state.agent.fps}")

    else:
        st.write("No video data available")


def show_audio_details():
    if st.session_state.agent is not None and st.session_state.agent.blob_url_audio is not None:

        st.subheader("Audio Details")
        st.write(f"Audio URL: {st.session_state.agent.blob_key_audio}")

        # get audio url with SAS token 
        st.audio(st.session_state.agent.blob_url_audio_with_sas, format="audio/wav")

        with st.expander(":blue[Transcription]"):
            st.markdown(st.session_state.agent.audio_transcription)

        with st.expander(":green[Summarization]"):
            st.markdown(st.session_state.agent.audio_summary)          

    else:
        st.write("No audio data available")


def display_raw_frame(frame):
    img_html = f"<img src='data:image/png;base64,{frame}'>"
    # img_html = f"<img src='data:image/png;base64,{frame}' class='img-fluid'>"
    st.markdown(
        img_html, unsafe_allow_html=True,
    )

def show_video_details():
    
    if st.session_state.agent is not None and st.session_state.agent.is_complete == True:
        
        # process the video
        for summary in st.session_state.agent.summarize_video():
            # print(summary)
            col_left, col_right = st.columns([1,2])
            
            with col_left:
                st.subheader("Frame")
                # st.image(summary.raw_data, use_column_width=True)
                # st.image(BytesIO(base64.b64decode(summary.raw_data)), use_column_width=True)

                # Get the SAS URL for the frame
                url = st.session_state.agent.get_video_frame_sas_url(summary.frame_id)
                st.image(url, use_column_width=True)
                # st.subheader(summary.frame_id)
                # display_raw_frame(summary.raw_data)

            with col_right:
                st.subheader(":blue[Summary]")
                st.markdown(summary.summary)

            st.divider()
            # st.rerun()


def main():

    st.set_page_config(page_title="ClipCognition", page_icon=":cinema:", layout="wide")

    # st.markdown("""
    #     <style>
    #         .appview-container .main .block-container {
    #             padding-top: 1rem;  # Adjust this value as needed
    #         }
    #     </style>
    # """, unsafe_allow_html=True)
    
    # Initialize Session state
    if "agent" not in st.session_state:
        st.session_state.agent = None

    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    st.header(":blue[Clip Cognition] :cinema:")
    st.markdown("##### Cognitive analysis of video content")
    
    # Sidebar configuration
    with st.sidebar:
        # label, cog = st.columns([3, 1])
        # with label:
        #     st.write(f"Selected Vector Store :blue[{st.session_state.vector_store}]")
        # with cog:
        #     with st.popover(":gear:"):
        #         st.session_state.vector_store = st.selectbox(
        #             "Vector Store",
        #             ("CosmosDB Mongo vCore", "CosmosDB NoSQL", "AI Search"),
        #         )
        
        st.session_state.vector_store = st.selectbox(
            ":blue[Vector Store]",
            options=[vector_store_type.value for vector_store_type in VectorStoreType]
        )

        video_file = st.file_uploader(
            "Upload a video :movie_camera:",
            # type=["mp4, wav"], 
            accept_multiple_files=False, 
            label_visibility="visible"
        )

        if video_file != None:

            # process the information from PDFs
            # with st.spinner("Processing..."):

            # Step 1: Get raw contents from video
            st.session_state.agent = VideoProcessingAgent(video_file, vector_store_type=st.session_state.vector_store)
            # To read file as bytes:
            video_data = video_file.getvalue()
            video_file_name = video_file.name
            
            # st.write(image_data)
            st.session_state.video_data = video_data
            st.video(st.session_state.video_data)

            if video_data != st.session_state.video_data:
                # perform cleanup
                st.session_state.frames = list()

            if st.button(":blue[Analyze]", type="secondary"):

                # process the video
                with st.spinner("Analyzing..."):

                    # Step 1: Get raw frames from video
                    st.session_state.agent.process_video()
                    st.info("Video processing complete!")
                    st.session_state.agent.is_complete = True
                    # st.rerun()
    
    tab_details, tab_audio, tab_video = st.tabs(["Details", "Audio", "Frames"])

    with tab_details:
        show_details()

    with tab_audio:
        show_audio_details()

    with tab_video:
        show_video_details()


if __name__ == "__main__":
    main()
