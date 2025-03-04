# Text2Voice

A Python script that takes your text input in English or French, corrects any typos using GPT-3.5, and reads the corrected text aloud using OpenAI's text-to-speech API with a male voice.

## Requirements

- Python 3.7 or higher
- OpenAI API key

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/text2voice.git
   cd text2voice
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   You can copy the `.env.example` file and replace the placeholder with your actual API key.

## Usage

Run the script:
```
python text2voice.py
```

1. Type your text in English or French when prompted.
2. The script will automatically detect the language, correct any typos using GPT-3.5, and read the corrected text aloud.
3. Type 'exit' to quit the program.

## Features

- Automatic language detection (English or French)
- Text correction using GPT-3.5
- Text-to-speech using OpenAI's TTS API with a male voice (Echo)
- Simple and interactive command-line interface

## Note

This script requires an internet connection to use the OpenAI API services. 