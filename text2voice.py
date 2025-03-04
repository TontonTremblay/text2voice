import os
import openai
import tempfile
import pygame
import readline
import atexit
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up command history - this file persists between sessions
HISTORY_FILE = os.path.expanduser("~/.text2voice_history")

def setup_history():
    """Set up command history for arrow key navigation with persistent storage."""
    # Create history file if it doesn't exist
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w'):
            pass
    
    # Read existing history from disk
    try:
        readline.read_history_file(HISTORY_FILE)
        print(f"Loaded command history from {HISTORY_FILE}")
    except FileNotFoundError:
        print("No previous command history found. Creating new history file.")
    
    # Set history length
    readline.set_history_length(100)
    
    # Save history on exit (as a backup)
    atexit.register(readline.write_history_file, HISTORY_FILE)

def save_history():
    """Save command history to disk immediately."""
    readline.write_history_file(HISTORY_FILE)

def correct_text(text):
    """Use GPT-3.5 to correct typos in the input text without translating."""
    # Explicitly instruct not to translate
    prompt = f"Fix ONLY typos and grammatical errors in this text. DO NOT translate it to another language. Keep the exact same language as the input: '{text}'"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a proofreader that ONLY fixes spelling and grammar mistakes. You NEVER translate between languages. If the input is in French, your output MUST be in French. If the input is in English, your output MUST be in English. Your only job is to fix typos and grammatical errors while keeping the exact same language as the input."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def text_to_speech(text):
    """Convert text to speech using OpenAI's TTS API with a male voice."""
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",  # Male voice
        input=text
    )
    
    # Save the audio to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    response.stream_to_file(temp_file.name)
    
    return temp_file.name

def play_audio(file_path):
    """Play the audio file."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.quit()
    os.unlink(file_path)  # Delete the temporary file

def main():
    # Set up command history
    setup_history()
    
    print("Welcome to Text2Voice!")
    print("Type your text in English or French, and I'll correct it and read it back to you.")
    print("Use up/down arrow keys to navigate through your command history.")
    print(f"Your command history is saved to {HISTORY_FILE} and persists between sessions.")
    print("Type 'exit' to quit.")
    
    while True:
        # Get user input (readline will handle arrow key navigation)
        text = input("\nEnter your text: ")
        
        # Save history immediately after each command
        save_history()
        
        if text.lower() == "exit":
            print("Goodbye!")
            break
        
        if not text:
            print("Please enter some text.")
            continue
        
        print("Correcting text...")
        
        # Correct the text
        corrected_text = correct_text(text)
        print(f"Corrected text: {corrected_text}")
        
        print("Converting to speech...")
        
        # Convert to speech
        audio_file = text_to_speech(corrected_text)
        
        print("Playing audio...")
        
        # Play the audio
        play_audio(audio_file)

if __name__ == "__main__":
    main() 