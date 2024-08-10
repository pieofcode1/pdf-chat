import os
import cv2
import uuid
from io import BytesIO
from moviepy.editor import VideoFileClip, AudioFileClip
import time
import base64
import numpy as np
from .storage_helper import StorageHelper
from .cosmos_util import CosmosUtil
from openai import AzureOpenAI
import requests
from typing import List
import urllib.request
from pydantic import BaseModel
from .schema import VideoFrameSummary, MediaAssetInfo
from .text_loader import generate_embeddings


class VideoProcessingAgent(object):
    def __init__(self, video_file, fps=5):
        self.id = str(uuid.uuid4())
        self.video_data = video_file.getvalue()
        self.audio_data = None
        self.is_complete = False
        self.fps = fps
        self.video_file_name = video_file.name
        self.blob_key_video = f"raw_files/video/{self.video_file_name}"
        self.blob_key_video_frame = f"raw_files/frames/{self.video_file_name}"
        self.blob_key_audio = f"raw_files/audio/{self.video_file_name.split('.')[0]}.mp3"
        self.blob_url_video = None
        self.blob_url_audio = None
        self.blob_url_frames = list()
        self.video_frames = list()
        self.audio_transcription: str = None
        self.audio_summary: str = None
        self.video_summary: str = None
        self.temp_folder = "./temp/"

        self._init_cosmos_util()
        self._init_storage_helper()
        self._init_openai_client()
        
    def _init_cosmos_util(self):
        self.cosmos_util = CosmosUtil(
            os.environ["AZURE_COSMOS_ENDPOINT"],
            os.environ["AZURE_COSMOS_KEY"],
            os.environ["AZURE_COSMOS_DATABASE_NAME"],
            os.environ["AZURE_COSMOS_CONTAINER_NAME"]
        )

        # Create the required containers
        self.cosmos_util.create_container_with_vectors("CC_VideoAssets", "/asset_name", ["/audio_summary_vector", "/video_summary_vector"])
        self.cosmos_util.create_container_with_vectors("CC_VideoAssetFrames", "/asset_name", ["/summary_vector"])
        # self.cosmos_util.add_containers([
        #       "CC_VideoAssets", 
        #       "CC_VideoAssetFrames", 
        #       "CC_VideoAssetAudio"])
        
    def _init_storage_helper(self):
        self.storage_helper = StorageHelper(
            os.environ["AZURE_STORAGE_CONNECTION_STRING"],
            os.environ["AZURE_STORAGE_CONTAINER_NAME"]
        )

    def _init_openai_client(self):
        azure_openai_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
        azure_openai_key = os.environ["AZURE_OPENAI_API_KEY"] if len(os.environ["AZURE_OPENAI_API_KEY"]) > 0 else None
        azure_openai_embedding_deployment = os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
        embedding_model_name = os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
        azure_openai_api_version = os.environ["OPENAI_API_VERSION"]
        gpt4o_deployment_name = os.environ["AZURE_GPT4_TURBO_DEPLOYMENT_NAME"]
        whisper_deployment_name = os.environ["AZURE_WHISPER_DEPLOYMENT_NAME"]
        tts_deployment_name = os.environ["AZURE_TTS_DEPLOYMENT_NAME"]

        self.aoai_client = AzureOpenAI(
            api_key=azure_openai_key,  
            api_version=azure_openai_api_version,
            azure_endpoint=azure_openai_endpoint
        )


    def upload_blob_from_stream(self, data, key):
        blob_url = self.storage_helper.upload_blob_from_stream(
            data, 
            key
        )
        return blob_url
    
    def upload_blob_from_file(self, file_path, key):
        blob_url = self.storage_helper.upload_blob_with_key(
            file_path, 
            key
        )
        return blob_url
    
    def get_video_frame_sas_url(self, frame_id):
        return self.storage_helper.generate_blob_sas_token(f"{self.blob_key_video_frame}/{frame_id}.png")
    
    def clip_video(self, start_time, end_time):
        clip = VideoFileClip(BytesIO(self.video_data))
        clip = clip.subclip(start_time, end_time)
        clip.write_videofile("clipped_video.mp4")
        # clip.write_videofile("subclip.mp4", codec="libx264")

        return clip

    def get_audio_from_video(self):
        clip = VideoFileClip(BytesIO(self.video_data))
        audio = clip.audio
        # audio.write_audiofile("audio.mp3", bitrate="32k")
        audio_data = audio_clip.to_soundarray()
        audio_clip = AudioFileClip(audio_data)

        return audio

    def process_video(self):
        # base_video_path, _ = os.path.splitext(video_path)

        # Upload video to blob storage
        self.blob_url_video = self.upload_blob_from_stream(self.video_data, self.blob_key_video)

        video_link = self.storage_helper.generate_blob_sas_token(self.blob_key_video)
        print(f"SAS Token Link: {video_link}")

        # video = cv2.VideoCapture(videoBytesIO(_path)
        # video_array = np.frombuffer(self.video_data, dtype=np.uint8)
        video = cv2.VideoCapture(video_link)
        # video.open(self.video_data)
        # video = cv2.VideoCapture(BytesIO(self.video_data), apiPreference=cv2.CAP_FFMPEG)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        frames_to_skip = int(fps * self.fps)
        curr_frame=0

        # Loop through the video and extract frames at specified sampling rate
        while curr_frame < total_frames - 1:
            video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            self.video_frames.append(base64.b64encode(buffer).decode("utf-8"))
            # base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
            curr_frame += frames_to_skip
        video.release()
        print(f"Extracted {len(self.video_frames)} frames")

        # Extract audio from video
        clip = VideoFileClip(video_link) 
        # clip = VideoFileClip(self.video_data)
        if clip.audio is None:
            print("No audio found in the video")
        else:
            print("Current working directory: ", os.getcwd())

            audio_path = f"{self.temp_folder}/{self.blob_key_audio}"
            self.create_directory_from_file_path(audio_path)
            clip.audio.write_audiofile(audio_path, bitrate="32k")
            # audio_data = clip.audio.to_soundarray()
            clip.audio.close()
            clip.close()

            # Get the absolute path
            absolute_path = os.path.abspath(audio_path)
            # Upload audio to blob storage
            self.blob_url_audio = self.upload_blob_from_file(absolute_path, self.blob_key_audio)
            self.blob_url_audio_with_sas = self.storage_helper.generate_blob_sas_token(self.blob_key_audio)
            
            print(f"Uploaded audio to {self.blob_url_audio}")
                       
            # Summarize the audio
            self.summarize_audio(absolute_path)

            # delete the local audio file
            # os.remove(absolute_path)
            # print(f"{absolute_path} has been successfully deleted.")

        # Upload video frames to blob storage
        self.upload_video_frames_to_blob(self.video_frames)

        # Add video asset to Cosmos DB
        video_asset = MediaAssetInfo(
            id=self.id,
            asset_name=self.video_file_name,
            blob_video_key=self.blob_key_video,
            blob_audio_key=self.blob_key_audio,
            blob_video_url=self.blob_url_video,
            blob_audio_url=self.blob_url_audio,
            frame_offset=self.fps,
            frame_count=len(self.video_frames),
            duration=self.fps * len(self.video_frames),
            total_frames=total_frames,
            audio_transcription=self.audio_transcription,
            audio_summary=self.audio_summary,
            audio_summary_vector=generate_embeddings(self.audio_summary) if (self.audio_summary) else None,
            video_summary=self.video_summary,
            video_summary_vector=generate_embeddings(self.video_summary) if (self.video_summary) else None,
        )
        video_asset_dict = video_asset.model_dump()
        self.cosmos_util.upsert_items("CC_VideoAssets", video_asset_dict)


        print("Video processing completed.")
        self.is_complete = True
    
    def upload_video_frames_to_blob(self, frames):
        for idx, frame in enumerate(frames):
            frame_name = f"{self.blob_key_video_frame}/{idx * self.fps}.png"
            url = self.upload_blob_from_stream(base64.b64decode(frame), frame_name)
            self.blob_url_frames.append(url)
    
    def create_directory_from_file_path(self, file_path):
        # Get the directory path from the file path
        directory_path = os.path.dirname(file_path)
        
        # Create the directory if it does not exist
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        else:
            print(f"Directory '{directory_path}' already exists.")

    def summarize_audio(self, audio_path):
        print("Summarizing audio...")
        gpt4o_deployment_name = os.environ["AZURE_GPT4_TURBO_DEPLOYMENT_NAME"]
        whisper_deployment_name = os.environ["AZURE_WHISPER_DEPLOYMENT_NAME"]

        # f = urllib.request.urlopen(self.blob_url_audio_with_sas)
        # audio_file = f.read()
        # f = requests.get(self.blob_url_audio_with_sas)
        # Transcribe the audio
        transcription = self.aoai_client.audio.transcriptions.create(
            model=whisper_deployment_name,
            file=open(audio_path, "rb"),
        )
        self.audio_transcription = transcription.text

        ## OPTIONAL: Uncomment the line below to print the transcription
        print("Transcript: ", transcription.text + "\n\n")

        response = self.aoai_client.chat.completions.create(
            model=gpt4o_deployment_name,
            messages=[
                {
                    "role": "system", 
                    "content":""""You are an expert in generating a transcript summary. Create a summary of the provided transcription. Respond in Markdown."""
                },
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": f"The audio transcription is: {transcription.text}"}
                    ],
                }
            ],
            temperature=0,
        )
        print(f"Summary: {response.choices[0].message.content}")
        self.audio_summary = response.choices[0].message.content

    def summarize_video(self):
        PROMPT_TEMPLATE = """

            You an expert in extracting scene by scene details from sequence of frames of the video. 
            While analyzing the frames, you are required to follow the following steps:

            - Understand the overall context of the frames and Generate a detailed Chapter Analysis of the video based on the frames provided.
            - Identify the scenes in each frame and build a detailed representation of the scenes.
            - Considering the context of the previous frames and current frame, create a dense Chapter, Scene and Action summary of the video in markdown format.
            - Never drop the context of the previous frames while analyzing the current frame.

            ### Previous Frame Scene Representation

            %s

        """
        print(f"Summarizing {len(self.video_frames)} frames...")
        gpt4o_deployment_name = os.environ["AZURE_GPT4_TURBO_DEPLOYMENT_NAME"]

        previous_context = ""
        index = 0
        for frame in self.video_frames:
            frame_url = self.blob_url_frames[index]
            frame_summary = VideoFrameSummary(id=str(uuid.uuid4()), frame_id=index * self.fps, asset_name=self.video_file_name, url=frame_url)
            print(f"Processing frame {frame_summary.frame_id}")
            response = self.aoai_client.chat.completions.create(
                model=gpt4o_deployment_name,
                messages=[
                    {
                        "role": "system", 
                        "content": PROMPT_TEMPLATE % previous_context
                    },
                    {
                        "role": "user", 
                        "content": [
                            {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{frame}', "detail": "low"}}
                        ],
                    }
                ],
                temperature=0,
            )
            previous_context = response.choices[0].message.content
            frame_summary.summary = previous_context
            frame_summary.summary_vector=generate_embeddings(previous_context) if (previous_context) else None,
            print(f"Frame Summary: {frame_summary.model_dump_json()}")
            frame_summary_dict = frame_summary.model_dump()
            self.cosmos_util.upsert_items("CC_VideoAssetFrames", frame_summary_dict)
            print(response.choices[0].message.content)
            index += 1
            yield frame_summary

