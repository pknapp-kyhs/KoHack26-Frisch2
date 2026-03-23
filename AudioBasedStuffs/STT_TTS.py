### Comments and documentation for teammates ###
# Import text-to-speech library for making the computer speak
import pyttsx3
# Import the transliteration module to convert Hebrew to English sounds
import AudioBasedStuffs.transliteration as transliteration
# Import Vosk for speech recognition
import vosk
# Import JSON to parse the speech recognition results
import json
# Import time for adding pauses
import time

###Speech-to-Text (STT) initialization ###
# Path to the Vosk speech recognition model
model_path = "vosk-model-small-en-us-0.15"
# Load the Vosk model
model = vosk.Model(model_path)
# Create a speech recognizer that listens at 16000 Hz sample rate
recognizer = vosk.KaldiRecognizer(model, 16000)

# Function that listens to microphone input and returns recognized text
def listen(data):
    # Check if the audio data contains recognized speech
    if recognizer.AcceptWaveform(data):
        # Get the recognition result from the recognizer
        result = recognizer.Result()
        # Parse the result as JSON and extract the text field
        text = json.loads(result)["text"]
        # If text was recognized
        if text:
            # Print what was recognized (for debugging)
            print(text)
            # Return the recognized text
            return text
        # If nothing was recognized, print None
        print(None)
        # Return None to indicate no recognition occurred
        return None

### Text-to-Speech (TTS) initialization ###
# Create a text-to-speech engine
engine = pyttsx3.init()
# Get all available voices on the system
voices = engine.getProperty('voices')
# Loop through voices to find one named "josh"
for voice in voices:
    if 'josh' in voice.name.lower():
        # Set the voice to the "josh" voice if found
        engine.setProperty('voice', voice.id)
        # Stop looking once we find it
        break
# Set the speech rate to 75 words per minute (slower is easier to understand)
engine.setProperty('rate', 75)
# Set the volume to maximum
engine.setProperty('volume', 1.0)

# Function to convert text to speech and play it
def speak(text):
    # Try to speak the text
    try:
        # Convert Hebrew text to English phonetic sounds for TTS
        text=transliteration.transliterate(text)
        # Tell the engine to say this text
        engine.say(text)
        # Wait for the speech to finish playing
        engine.runAndWait()
                
    except Exception as e:
        # If there's an error, print the error message
        print(f"(TTS Error: {e})")
    finally:
        # Add a short pause after speaking to prevent the microphone from picking up the speaker's own voice
        time.sleep(0.5)

# If this script is run directly (not imported as a module)
if __name__ == "__main__":
    # Loop forever, continuously listening and echoing
    while True:
        # Listen for speech and get the recognized text
        text = listen()
        # If text was recognized
        if text:
            # Print what was heard
            print("You said:", text)
