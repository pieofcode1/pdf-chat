import os
import streamlit as st
from pathlib import Path
import dotenv
from framework.text_loader import *
import azure.cognitiveservices.speech as speechsdk


env_name = os.environ["APP_ENV"] if "APP_ENV" in os.environ else "local"

# Load env settings
env_file_path = Path(f"./.env.{env_name}")
print(f"Loading environment from: {env_file_path}")
with open(env_file_path) as f:
    dotenv.load_dotenv(dotenv_path=env_file_path)
# print(os.environ)

# Set up Azure Speech Service credentials
speech_key = os.environ["COGNITIVE_MULTISVC_API_KEY"]
service_region = os.environ["COGNITIVE_MULTISVC_REGION"]


def speech_recognize_once_from_mic():
    # Set up the speech config and audio config
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.AudioConfig(use_default_microphone=True)

    # Create a speech recognizer with the given settings
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    st.write("Speak into your microphone.")
    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return f"Recognized: {result.text}"
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "No speech could be recognized"
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        return f"Speech Recognition canceled: {cancellation_details.reason}"
    else:
        return "Unknown error"
    

def main():

    st.set_page_config(page_title="Bing Web Search", page_icon=":books:")

    st.title("Azure Speech Service with Streamlit")

    if st.button('Start speech recognition'):
        recognition_result = speech_recognize_once_from_mic()
        st.write(recognition_result)
    

if __name__ == "__main__":
    main()
