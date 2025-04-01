import pyttsx3
import multiprocessing
import time

# Global variable to store speech process
speech_process = None

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def say(text):
    global speech_process
    stop_speech()  # Stop any ongoing speech before starting new one
    speech_process = multiprocessing.Process(target=speak_text, args=(text,))
    speech_process.start()

def stop_speech():
    global speech_process
    if speech_process and speech_process.is_alive():
        speech_process.terminate()
        speech_process.join()
        speech_process = None
        return True  # Indicate success
    return False  # No speech was running


# Example Usage
if __name__ == "__main__":
    say("Hello, this is a text to speech test.")
    time.sleep(2)  # Allow some speech to play
    stop_speech()  # Stop speech midway
