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
- **Flask** 
- **Azure Cognitive Services** subscription for Text Analytics and Text-to-Speech APIs
- **OpenAI API key** (for GPT-3 or GPT-4)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/AnupriyaHaridas/AI-FeedbackGenie.git
    cd AI-FeedbackGenie
    ```

2. **Create virtual environment**:
    First, make sure you have Python installed. You can create a virtual environment for the project using the command:

    ```bash
    python -m venv venv
    ```

3. **Activate virtual environment**:
    
    On Windows: 

    ```bash
    .\venv\Scripts\activate
    ```

    On On macOS/Linux: 
    ```bash
    source venv/bin/activate
    ```

4. **Install required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Set up environment variables**:  
    Create a `.env` file in the project directory with the following keys:
    ```env
    AZURE_TEXT_ANALYTICS_KEY=your_azure_text_analytics_key  # Replace with your key
    AZURE_TEXT_ANALYTICS_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
    OPENAI_API_KEY=your_openai_api_key
    AZURE_REGION=your_azure_region
    AZURE_TTS_KEY=your_azure_text_to_speech_key
    AZURE_TTS_ENDPOINT=https://your-region.tts.speech.microsoft.com/cognitiveservices/v1
    OPENAI_MODEL=gpt-4  # Default model
    MODEL_TEMPERATURE=0.7  # Adjust for randomness
    MODEL_MAX_TOKENS=150  # Adjust for response length

    ```

6. **Run the application**:
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

```

## Live Demo 🌐  
Check out the hosted application here: [AI Feedback Genie 🚀](https://ai-feedbackgenie.onrender.com)
