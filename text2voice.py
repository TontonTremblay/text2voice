import os
import openai
import tempfile
import pygame
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def correct_text(text, language):
    """Use GPT-3.5 to correct typos in the input text."""
    if language.lower() == "english":
        prompt = f"Please correct any typos or grammatical errors in this English text, but preserve the meaning: '{text}'"
    else:  # French
        prompt = f"Veuillez corriger les fautes de frappe ou les erreurs grammaticales dans ce texte français, mais préservez le sens: '{text}'"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that corrects text while preserving its meaning."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def text_to_speech(text):
    """Convert text to speech using OpenAI's TTS API with a male voice."""
    response = openai.audio.speech.create(
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
    print("Welcome to Text2Voice!")
    print("Type your text in English or French, and I'll correct it and read it back to you.")
    print("Type 'exit' to quit.")
    
    while True:
        # Get user input
        text = input("\nEnter your text: ")
        
        if text.lower() == "exit":
            print("Goodbye!")
            break
        
        if not text:
            print("Please enter some text.")
            continue
        
        # Detect language (simple detection based on common French words)
        french_words = ["je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "le", "la", "les", "un", "une", "des", "et", "ou", "mais", "donc", "car", "pour", "avec", "sans", "dans", "sur", "sous"]
        french_word_count = sum(1 for word in text.lower().split() if word in french_words)
        language = "french" if french_word_count / max(1, len(text.split())) > 0.2 else "english"
        
        print(f"Detected language: {language.capitalize()}")
        print("Correcting text...")
        
        # Correct the text
        corrected_text = correct_text(text, language)
        print(f"Corrected text: {corrected_text}")
        
        print("Converting to speech...")
        
        # Convert to speech
        audio_file = text_to_speech(corrected_text)
        
        print("Playing audio...")
        
        # Play the audio
        play_audio(audio_file)

if __name__ == "__main__":
    main() 