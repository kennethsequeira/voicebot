# reference code: https://www.youtube.com/watch?v=I08pmoEMiqU
import os
import azure.cognitiveservices.speech as speechsdk
import openai
from openai import OpenAI

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API credentials
openai.api_type = "azure"
#openai.apibase = os.environ.get("OPENAI_ENDPOINT")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Set up engine name
engine_name = "test"
MODEL="gpt-4o"

# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = os.environ.get("AZURE_SPEECH_KEY")
service_region = "centralindia"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Set up Azure Text-to-Speech language 
speech_config.speech_synthesis_language = "en-IN"
# Set up Azure Speech-to-Text language recognition
speech_config.speech_recognition_language = "en-IN"

# Set up the voice configuration
speech_config.speech_synthesis_voice_name = "en-IN-AashiNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Define the speech-to-text function
def speech_to_text():
    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # Create a speech recognizer and start the recognition
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Say something...")

    #result = speech_recognizer.recognize_once_async().get()
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
    #if speech_recognizer.recognize_once_async().get()
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "Sorry, I didn't catch that."
    elif result.reason == speechsdk.ResultReason.Canceled:
        return "Recognition canceled."

# Define the text-to-speech function
def text_to_speech(text):
    try:
        result = speech_synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Text-to-speech conversion successful.")
            return True
        else:
            print(f"Error synthesizing audio: {result}")
            return False
    except Exception as ex:
        print(f"Error synthesizing audio: {ex}")
        return False

# Define the Azure OpenAI language generation function
def generate_text(prompt):
    
    #response = openai.ChatCompletion.create(
    response = client.chat.completions.create(
        model=MODEL,
        #engine=engine_name,
        messages=[
            {"role": "system", "content": "You are an AI assistant that helps people find information."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    #return response['choices'][0]['message']['content']
    return response.choices[0].message.content


# Main program loop
while True:
    # Get input from user using speech-to-text
    user_input = speech_to_text()
    print(f"You said: {user_input}")

    # Generate a response using OpenAI
    prompt = f"Q: {user_input}\nA:"
    response = generate_text(prompt)
    #response = user_input
    print(f"AI says: {response}")

    # Convert the response to speech using text-to-speech
    text_to_speech(response)