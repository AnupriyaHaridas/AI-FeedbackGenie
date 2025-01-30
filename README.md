# AI-FeedbackGenie

## Overview

This web application allows users to submit feedback, which is then analyzed for sentiment using **Azure Cognitive Services**. Based on the sentiment of the feedback, the system generates an appropriate response using an **LLM** (such as **GPT-3** or **GPT-4**) and converts the response into audio using **Azure's Text-to-Speech** service.

---

## Technologies Used

- **Backend**: Python with Flask
- **Frontend**: HTML, CSS (Optional: React can be used if preferred)
- **Sentiment Analysis**: Azure Text Analytics API
- **Text-to-Speech**: Azure Text-to-Speech API
- **Language Model**: OpenAI's GPT-3 or GPT-4 API

---

## Setup Instructions

### Prerequisites

Ensure the following are installed:
- **Python 3.x**
- **Flask** (or **Django**)
- **Azure Cognitive Services** subscription for Text Analytics and Text-to-Speech APIs
- **OpenAI API key** (for GPT-3 or GPT-4)

### Installation

1. **Clone the repository**:
    ```bash
    git clone origin https://github.com/AnupriyaHaridas/AI-FeedbackGenie.git
    cd AI-FeedbackGenie
    ```

2. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables**:  
Create a `.env` file in the project directory with the following keys:
    ```env
    AZURE_KEY=<your_azure_text_analytics_key>
    AZURE_ENDPOINT=<your_azure_text_analytics_endpoint>
    OPENAI_API_KEY=<your_openai_api_key>
    AZURE_REGION=eastus
    AZURE_TTS_KEY=<your_azure_text_to_speech_key>
    AZURE_TTS_ENDPOINT=<your_azure_text_to_speech_endpoint>
    
    ```

4. **Run the application**:
    ```bash
    python app.py
    ```
   The application will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

## File Structure

```bash
/project
│		/venv
├── /templates
│   └── index.html
├── /static
│   └── /audio
		└── /css
				└── /styles.css
├── app.py
├── requirements.txt
├── .env
└── README.md
