import os
import threading
import tempfile
import time
import uuid
from gtts import gTTS
import pygame

# Global variables
speech_active = False
current_speech_id = None
temp_files = []  # Track temp files for cleanup

def text_to_speech(text):
    """Converts text to speech using gTTS and pygame for playback."""
    global speech_active, current_speech_id
    
    if not text or text.strip() == "":
        return False
        
    # Stop any currently playing speech
    stop_speech()
    
    # Create a unique speech ID
    speech_id = str(uuid.uuid4())
    current_speech_id = speech_id
    
    # Start speech processing in a new thread
    speech_thread = threading.Thread(target=_process_and_play, args=(text, speech_id))
    speech_thread.daemon = True
    speech_thread.start()
    
    return True

def _process_and_play(text, speech_id):
    """Internal function to process text and play it."""
    global speech_active, current_speech_id, temp_files
    
    temp_filename = None
    
    try:
        # Make sure pygame is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Create a temporary file with unique name to avoid conflicts
        temp_filename = os.path.join(tempfile.gettempdir(), f"speech_{speech_id}.mp3")
        temp_files.append(temp_filename)  # Track for cleanup
        
        # Generate speech file
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(temp_filename)
        
        # Check if this speech request is still current
        if speech_id != current_speech_id:
            return
        
        # Play the speech
        speech_active = True
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        
        # Wait for playback to finish or be interrupted
        while pygame.mixer.music.get_busy() and speech_id == current_speech_id:
            pygame.time.Clock().tick(10)
        
        # Clean up
        pygame.mixer.music.stop()
        
    except Exception as e:
        print(f"Speech processing error: {e}")
    
    finally:
        speech_active = False
        # Cleanup attempted here but might fail if file is in use
        _cleanup_temp_files()

def stop_speech():
    """Stops any ongoing speech."""
    global speech_active, current_speech_id
    
    if not speech_active:
        return True  # Already stopped
    
    try:
        # Change the speech ID to invalidate any ongoing speech
        current_speech_id = None
        
        # Stop pygame playback if it's playing
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        speech_active = False
        print("Speech stopped successfully")
        
        # Attempt cleanup
        _cleanup_temp_files()
        
        return True
    
    except Exception as e:
        print(f"Error stopping speech: {e}")
        return False

def _cleanup_temp_files():
    """Helper function to clean up temporary files."""
    global temp_files
    
    files_to_remove = temp_files.copy()
    temp_files = []
    
    for file in files_to_remove:
        try:
            if os.path.exists(file):
                os.unlink(file)
        except Exception as e:
            # If file is still in use, add it back to the list for later cleanup
            temp_files.append(file)
            print(f"Could not remove temp file {file}: {e}")

# Initialize pygame mixer on module import
try:
    pygame.mixer.init()
    print("Pygame mixer initialized successfully")
except Exception as e:
    print(f"Could not initialize pygame mixer: {e}")