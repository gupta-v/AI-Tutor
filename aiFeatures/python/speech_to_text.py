import speech_recognition as sr

# Global variable to track if we should stop listening
stop_listening = False

def speech_to_text():
    """Converts speech to text using SpeechRecognition with ability to stop"""
    global stop_listening
    stop_listening = False
    
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source: 
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            print("\nListening...", flush=True)
            
            # Set a timeout to check periodically if we should stop
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            # If stop_listening was set to True during recognition, return empty
            if stop_listening:
                return ""
                
            print("\nRecognizing...", flush=True)
            query = recognizer.recognize_google(audio, language="en-in")
            return query
            
    except sr.UnknownValueError:
        print("\nSorry, I couldn't understand what you said.", flush=True)
        return ""
    except sr.RequestError as e:
        print(f"\nCould not request results from Google Speech Recognition service; {e}", flush=True)
        return ""
    except Exception as e:
        print(f"\nAn error occurred: {e}", flush=True)
        return ""

def stop_speech_recognition():
    """Stops the speech recognition process."""
    global stop_listening
    stop_listening = True
    print("Speech recognition stopped by user")

# Test Run
if __name__ == "__main__":
    print("Transcribed Text:", speech_to_text())