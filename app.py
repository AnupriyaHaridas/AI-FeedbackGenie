import os
import openai
import requests, time
from flask import Flask, request, render_template, send_file, redirect, url_for
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Initialize the Flask app
app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Retrieve API keys and endpoints from environment variables
AZURE_TEXT_ANALYTICS_KEY = os.getenv('AZURE_TEXT_ANALYTICS_KEY')
AZURE_TEXT_ANALYTICS_ENDPOINT = os.getenv('AZURE_TEXT_ANALYTICS_ENDPOINT')

AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
AZURE_TTS_ENDPOINT = os.getenv("AZURE_TTS_ENDPOINT")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Headers for OpenAI API requests
headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

# Folder to save audio files
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Function to authenticate the client for Azure Text Analytics API
def authenticate_client():
    return TextAnalyticsClient(endpoint=AZURE_TEXT_ANALYTICS_ENDPOINT, credential=AzureKeyCredential(AZURE_TEXT_ANALYTICS_KEY))

# Function to analyze sentiment of text using Azure's Text Analytics API
def analyze_sentiment(text):
    client = authenticate_client()
    documents = [text]
    try:
        response = client.analyze_sentiment(documents=documents)[0]
        return {
            "sentiment": response.sentiment,
            "positive_score": response.confidence_scores.positive,
            "neutral_score": response.confidence_scores.neutral,
            "negative_score": response.confidence_scores.negative
        }
    except Exception as e:
        return {"error": str(e)}

# Function to generate a response using OpenAI GPT-4 based on feedback sentiment
def generate_gpt4_response(feedback, sentiment):

    if sentiment == 'positive':
        prompt = f"The user gave positive feedback: '{feedback}'. Please generate a thankful and enthusiastic response."
    elif sentiment == 'negative':
        prompt = f"The user gave negative feedback: '{feedback}'. Please generate a polite and empathetic response to apologize and offer help."
    else:
        prompt = f"The user gave neutral feedback: '{feedback}'. Please generate a neutral and informative response."

    # Load model parameters from .env file; use default values if not set to prevent errors
    data = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens":int(os.getenv("MODEL_MAX_TOKENS", 150)),
        "temperature":float(os.getenv("MODEL_TEMPERATURE", 0.7))
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, verify=False)
        response.raise_for_status()
        ai_response = response.json()
        return ai_response['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"❌ OpenAI API error: {str(e)}"


# Function to convert text to speech using Azure TTS (Text-to-Speech) service
def text_to_speech(text, sentiment):
    
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, region=AZURE_REGION) # Set up the speech configuration
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural" 
    
    if sentiment == "positive":
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # Cheerful, upbeat voice
    elif sentiment == "negative":
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"  # Calm, concerned voice
    else:
        speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"  # Neutral tone

    # Generate a unique filename for the audio
    audio_filename = f"response_{sentiment}_{int(time.time())}.mp3"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)

    # Set up audio configuration (output to a file)
    audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_path)   
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output) 
    synthesizer.speak_text_async(text).get()

    return audio_filename
  

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None
    sentiment_result = None
    gpt4_response = None

    if request.method == "POST":
        user_input = request.form["feedback"]
        sentiment_result = analyze_sentiment(user_input)    # Sentiment Analysis
        
        if sentiment_result:
            gpt4_response = generate_gpt4_response(user_input, sentiment_result['sentiment'])    # Generate GPT-4 response based on the sentiment
            audio_filename = text_to_speech(gpt4_response, sentiment_result['sentiment'])   # Convert the AI response to speech
            print(f"Generated Response: {gpt4_response}")   # success
        else:
            print("Could not analyze sentiment.")   # failure

        return render_template(
            "index.html",
            feedback=user_input,
            sentiment=sentiment_result,
            ai_response=gpt4_response,
            audio_filename=audio_filename
        )
    return render_template("index.html", feedback=None, sentiment=None, ai_response=None)


# Generates audio file for playback or download.
@app.route("/download_audio/<filename>")
def download_audio(filename):
    audio_path = os.path.join(AUDIO_FOLDER, filename)
    return send_file(audio_path, as_attachment=True)


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
