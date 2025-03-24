import pyttsx3

def text_to_speech(text): 
    """Converts text to speech using pyttsx3, creating a new instance each time."""
    if not text:
        return
    
    engine = pyttsx3.init()

    # Use the Microsoft Speech API for more voices (Windows)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index if needed
    # Set the speech rate (default is usually ~200 words per minute)
    rate = engine.getProperty('rate')  # Get the current rate
    engine.setProperty('rate', rate - 25)  # Decrease the rate for slower speech

    engine.say(text)
    engine.runAndWait()
    
    
# Test Run
if __name__ == "__main__":
    user_text = input("Enter text to speak: ")
    text_to_speech(user_text)
