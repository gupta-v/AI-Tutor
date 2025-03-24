import os
import sys
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from aiFeatures.python.ai_response import generate_response
from aiFeatures.python.speech_to_text import speech_to_text, stop_speech_recognition
from aiFeatures.python.text_to_speech import text_to_speech
import pyttsx3

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    """Handles text/voice input and returns AI response."""
    data = request.json
    user_query = data.get("query")

    if not user_query:
        return jsonify({"error": "No input provided"}), 400

    response = generate_response(user_query)

    # Speak the response in a separate thread
    def speak():
        text_to_speech(response)  # New instance of pyttsx3 created each time

    speak_thread = threading.Thread(target=speak)
    speak_thread.start()

    return jsonify({"response": response})

@app.route("/speech-to-text", methods=["POST"])
def process_voice():
    """Handles voice input and converts it to text."""
    user_query = speech_to_text()
    return jsonify({"query": user_query})

@app.route("/stop-speech", methods=["POST"])
def stop_speech():
    """Stops ongoing speech by reinitializing pyttsx3 and stopping."""
    # Stop text-to-speech output
    engine = pyttsx3.init()
    engine.stop()
    return jsonify({"message": "Speech stopped"})

@app.route("/stop-listening", methods=["POST"])
def stop_listening():
    """Stops the speech recognition process."""
    stop_speech_recognition()
    return jsonify({"message": "Listening stopped"})

if __name__ == "__main__":
    app.run(debug=True)