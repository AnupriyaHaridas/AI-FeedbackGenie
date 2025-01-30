import os
import openai, requests
from flask import Flask, request, render_template, send_file
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Get API keys from environment variables
AZURE_KEY = os.getenv('AZURE_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')


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
        
        return render_template(
            "index.html",
            feedback=user_input,
            sentiment=sentiment_result
        )

    return render_template("index.html", feedback=None, sentiment=None, ai_response=None)

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
