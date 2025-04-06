import os
import re
import sys
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import threading
import tempfile

# Add aiFeatures/python to sys.path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from aiFeatures.python.ai_response import generate_response_without_retrieval, generate_response_with_retrieval, ChatSessionManager
from aiFeatures.python.speech_to_text import speech_to_text
from aiFeatures.python.text_to_speech import say, stop_speech
from aiFeatures.python.web_scraping import web_response
from aiFeatures.python.rag_pipeline import index_pdfs, retrieve_answer

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Add a secret key for sessions
CORS(app)  # Enable CORS for frontend requests

# Global variables
vector_store = None
session_manager = ChatSessionManager()
default_session_id = "user_session_001"  # Default session ID

import re


def chunk_text(text, max_length=150):
    """Split text into smaller chunks at sentence boundaries for faster TTS processing."""
    # Split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/clear-session", methods=["POST"])
def clear_session():
    """Clears the current RAG session and resets the vector store."""
    global vector_store, session_manager
    
    try:
        # Reset the vector store
        vector_store = None
        
        # Clear the session for this user
        session_manager.delete_session(default_session_id)
        
        return jsonify({"success": True, "message": "Session cleared successfully"})
    
    except Exception as e:
        print(f"Error clearing session: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/initialize-rag", methods=["POST"])
def initialize_rag():
    """Handles indexing PDFs from uploaded files or a folder path."""
    global vector_store
    
    try:
        if 'files' in request.files:
            files = request.files.getlist('files')
            
            with tempfile.TemporaryDirectory() as temp_dir:
                file_paths = []
                for file in files:
                    if file.filename.endswith('.pdf'):
                        file_path = os.path.join(temp_dir, file.filename)
                        file.save(file_path)
                        file_paths.append(file_path)

                if len(file_paths) == 1:
                    vector_store = index_pdfs(file_paths[0])  # Using unified index_pdfs function
                else:
                    vector_store = index_pdfs(file_paths)  # Using unified index_pdfs function
        
        elif 'folder' in request.form:
            folder_path = request.form.get('folder')
            vector_store = index_pdfs(folder_path)  # Using unified index_pdfs function
        
        else:
            return jsonify({"success": False, "message": "No files or folder provided"}), 400
        
        return jsonify({"success": True, "message": "RAG initialized successfully"})
    
    except Exception as e:
        print(f"RAG initialization error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    """Handles text input and returns AI response with chat history management."""
    global vector_store, session_manager, default_session_id
    data = request.json
    user_query = data.get("query")

    if not user_query:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Get retrieved information if vector store exists
        retrieved_info = retrieve_answer(user_query, vector_store) if vector_store else ""
        
        # Generate response based on whether retrieval was performed
        if retrieved_info:
            response = generate_response_with_retrieval(
                default_session_id, 
                user_query,
                retrieved_info, 
                session_manager
            )
            
            say(response)  # Convert response to speech

            return jsonify({
                "response": response,
                "retrieved": retrieved_info,
                "hasRetrieval": bool(retrieved_info)
            })
            
        else:
            scraped_text = web_response(user_query)  # Call web scraping function
            response = generate_response_without_retrieval(
                default_session_id, 
                user_query, 
                scraped_text,
                session_manager
            )
            say(response)  # Convert response to speech

            return jsonify({
                "response": response,
                "scraped": scraped_text,
                "hasScraping": bool(scraped_text)
            })
    
    except Exception as e:
        print(f"Error processing query: {e}")
        return jsonify({"error": f"Failed to process query: {str(e)}"}), 500
    
@app.route("/speech-to-text", methods=["POST"])
def process_voice():
    """Handles voice input and converts it to text."""
    try:
        user_query = speech_to_text()
        return jsonify({"query": user_query})
    except Exception as e:
        print(f"Speech recognition error: {e}")
        return jsonify({"error": f"Failed to recognize speech: {str(e)}"}), 500

@app.route("/text-to-speech", methods=["POST"])
def process_speech():
    """Converts text to speech."""
    data = request.json
    text = data.get("text")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        say(text)  # Convert text to speech
        return jsonify({"success": True})
    except Exception as e:
        print(f"Text-to-speech error: {e}")
        return jsonify({"error": f"Failed to convert text to speech: {str(e)}"}), 500
    
    
@app.route("/stop-speech", methods=["POST"])
def handle_stop_speech():
    """Stops ongoing speech output."""
    try:
        success = stop_speech()
        return jsonify({"message": "Speech stopped", "success": success})
    except Exception as e:
        print(f"Error stopping speech: {e}")
        return jsonify({"error": f"Failed to stop speech: {str(e)}"}), 500

    
if __name__ == "__main__":
    app.run(debug=True)