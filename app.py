import os
import openai, requests
from flask import Flask, request, render_template
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

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

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
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
            print(f"Generated Response: {gpt4_response}")
        else:
            print("Could not analyze sentiment.")

        return render_template(
            "index.html",
            feedback=user_input,
            sentiment=sentiment_result,
            ai_response=gpt4_response
        )

    return render_template("index.html", feedback=None, sentiment=None, ai_response=None)

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
