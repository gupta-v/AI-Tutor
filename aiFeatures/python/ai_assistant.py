import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "aiFeatures/python")))

from ai_response import generate_response
from speech_to_text import speech_to_text
from text_to_speech import text_to_speech
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

def main():
    print("\nWelcome to AI Assistant!")
    mode = input("\nChoose mode (text/voice): ").strip().lower()

    if mode == "text":
        user_input = input("\nType your question: ")
    elif mode == "voice":
        print("\nSpeak now...")
        user_input = speech_to_text()
        print("You said:", user_input)
    else:
        print("\nInvalid mode. Choose 'text' or 'voice'.")
        return

    # Get AI response
    response = generate_response(user_input)
    print("\nAI Response:", response)

    # Speak the response if in voice mode
    if mode == "voice":
        text_to_speech(response)

if __name__ == "__main__":
    main()
