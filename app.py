import os
import openai
import requests
from flask import Flask, request, render_template, send_file
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Get API keys from environment variables
AZURE_KEY = os.getenv('AZURE_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
SPEECH_ENDPOINT = os.getenv("SPEECH_ENDPOINT")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

# Folder to save audio files
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)


def authenticate_client():
    return TextAnalyticsClient(endpoint=AZURE_ENDPOINT, credential=AzureKeyCredential(AZURE_KEY))


def analyze_sentiment(text):
    client = authenticate_client()
    documents = [text]
    response = client.analyze_sentiment(documents=documents)[0]

    return {
        "sentiment": response.sentiment,
        "positive_score": response.confidence_scores.positive,
        "neutral_score": response.confidence_scores.neutral,
        "negative_score": response.confidence_scores.negative
    }


def generate_gpt4_response(feedback, sentiment):
    if sentiment == 'positive':
        prompt = f"The user gave positive feedback: '{feedback}'. Please generate a thankful and enthusiastic response."
    elif sentiment == 'negative':
        prompt = f"The user gave negative feedback: '{feedback}'. Please generate a polite and empathetic response to apologize and offer help."
    else:
        prompt = f"The user gave neutral feedback: '{feedback}'. Please generate a neutral and informative response."

    data = {
        "model": "gpt-4",  # Use GPT-4 model for sentiment analysis
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens":150,
        "temperature":0.7
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, verify=False)
        response.raise_for_status()  # Raise an error for bad responses
        ai_response = response.json()
        ai_sentiment = ai_response['choices'][0]['message']['content']  # Extract the sentiment

        return ai_sentiment

    except requests.exceptions.RequestException as e:
        return f"❌ Error: {str(e)}"


def text_to_speech(text, sentiment):
    # Set up the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # Default voice for neutral tone
    
    # Adjust voice based on sentiment
    if sentiment == "positive":
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # Cheerful, upbeat voice
    elif sentiment == "negative":
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"  # Calm, concerned voice
    else:
        speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"  # Neutral tone

    # Generate a unique filename for the audio
    audio_filename = f"response_{sentiment}.mp3"
    audio_path = os.path.join(AUDIO_FOLDER, audio_filename)

    # Set up audio configuration (output to a file)
    audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_path)

    # Create a synthesizer and synthesize speech
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    synthesizer.speak_text_async(text).get()

    return audio_filename  # Return the filename for frontend use

    

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None
    sentiment_result = None
    gpt4_response = None

    if request.method == "POST":
        user_input = request.form["feedback"]
        
        # Sentiment Analysis
        sentiment_result = analyze_sentiment(user_input)
        
        if sentiment_result:
            # Generate GPT-4 response based on the sentiment
            gpt4_response = generate_gpt4_response(user_input, sentiment_result)
            # Convert the AI response to speech
            audio_filename = text_to_speech(gpt4_response, sentiment_result['sentiment'])
            print(f"Generated Response: {gpt4_response}")# success
        else:
            print("Could not analyze sentiment.")# failure

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
