import os
import openai
import tempfile
import pygame
import readline
import atexit
import hashlib
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up command history - this file persists between sessions
HISTORY_FILE = os.path.expanduser("~/.text2voice_history")

# Set up cache directory for audio files
CACHE_DIR = os.path.expanduser("~/.text2voice_cache")
CACHE_INDEX_FILE = os.path.join(CACHE_DIR, "cache_index.json")

def setup_cache():
    """Set up the cache directory for storing audio files."""
    # Create cache directory if it doesn't exist
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
        print(f"Created cache directory at {CACHE_DIR}")
    
    # Create or load cache index
    if not os.path.exists(CACHE_INDEX_FILE):
        with open(CACHE_INDEX_FILE, 'w') as f:
            json.dump({}, f)
        print("Created new cache index file")
        return {}
    
    # Load existing cache index
    try:
        with open(CACHE_INDEX_FILE, 'r') as f:
            cache_index = json.load(f)
        print(f"Loaded cache index with {len(cache_index)} entries")
        return cache_index
    except json.JSONDecodeError:
        print("Cache index file corrupted. Creating new one.")
        with open(CACHE_INDEX_FILE, 'w') as f:
            json.dump({}, f)
        return {}

def save_cache_index(cache_index):
    """Save the cache index to disk."""
    with open(CACHE_INDEX_FILE, 'w') as f:
        json.dump(cache_index, f)

def get_text_hash(text):
    """Generate a hash for the text to use as a cache key."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

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

def text_to_speech(text, cache_index):
    """Convert text to speech using OpenAI's TTS API with a male voice or use cached version if available."""
    # Check if we have this text cached
    text_hash = get_text_hash(text)
    
    if text_hash in cache_index:
        cached_file_path = cache_index[text_hash]
        # Verify the file exists
        if os.path.exists(cached_file_path):
            print("Using cached audio file")
            return cached_file_path
    
    print("Generating new audio file with OpenAI TTS")
    # Not in cache, generate new audio
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",  # Male voice
        input=text
    )
    
    # Save to a permanent file in the cache directory
    cache_file_path = os.path.join(CACHE_DIR, f"{text_hash}.mp3")
    response.stream_to_file(cache_file_path)
    
    # Update cache index
    cache_index[text_hash] = cache_file_path
    save_cache_index(cache_index)
    
    return cache_file_path

def play_audio(file_path, is_cached=True):
    """Play the audio file."""
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.quit()
    
    # Only delete temporary files, not cached ones
    if not is_cached:
        os.unlink(file_path)  # Delete the temporary file

def main():
    # Set up command history and cache
    setup_history()
    cache_index = setup_cache()
    
    print("Welcome to Text2Voice!")
    print("Type your text in English or French, and I'll correct it and read it back to you.")
    print("Use up/down arrow keys to navigate through your command history.")
    print(f"Your command history is saved to {HISTORY_FILE} and persists between sessions.")
    print(f"Audio files are cached in {CACHE_DIR} for faster replay of repeated inputs.")
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
        
        # Convert to speech (or use cached version)
        audio_file = text_to_speech(corrected_text, cache_index)
        
        print("Playing audio...")
        
        # Play the audio
        play_audio(audio_file, is_cached=True)

if __name__ == "__main__":
    main() 