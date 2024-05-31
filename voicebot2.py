# voicebot.py

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer, SpeechSynthesizer, SpeechSynthesisOutputFormat
import openai
import logging
import os

# Initialize Flask app
app = Flask(__name__)

# Initialize logging
logging.basicConfig(filename='voicebot.log', level=logging.INFO)

# Initialize Microsoft Speech SDK
def initialize_speech_sdk():
    try:
        subscription_key = os.environ['AZURE_SPEECH_KEY']
        region = "centralindia"

        speech_config = SpeechConfig(subscription=subscription_key, region=region)
        audio_config = AudioConfig(use_default_microphone=True)
        recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        return recognizer, synthesizer
    except Exception as e:
        logging.error(f"Error initializing Speech SDK: {e}")
        return None, None

speech_recognizer, speech_synthesizer = initialize_speech_sdk()

# Initialize GPT-4O
def initialize_openai():
    try:
        openai.api_key = os.environ['OPENAI_KEY']
    except Exception as e:
        logging.error(f"Error initializing OpenAI: {e}")

initialize_openai()

# Define route for handling incoming calls
@app.route("/voicebot2", methods=['GET','POST'])
def voicebot():
    try:
        # Get the speech input from the incoming call
        speech_input = request.values.get('SpeechResult')
        
        # Use GPT-4O to generate a response
        response = openai.Completion.create(model="text-davinci-004", prompt=speech_input, max_tokens=50)
        generated_response = response.choices[0].text.strip()
        
        # Synthesize the response
        synthesized_response = speech_synthesizer.speak_text_async(generated_response).get()
        
        # Construct TwiML response with synthesized speech
        twiml_response = VoiceResponse()
        twiml_response.say(synthesized_response.audio_data, voice='alice')
        
        return str(twiml_response)

    except Exception as e:
        logging.error(f"Error handling voicebot request: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)
