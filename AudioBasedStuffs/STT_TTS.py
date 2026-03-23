### Comments and documentation for teammates ###
# Import text-to-speech library for making the computer speak
import pyttsx3
# Import the transliteration module to convert Hebrew to English sounds
import AudioBasedStuffs.transliteration as transliteration
# Import Vosk for speech recognition
import vosk
import json
import time
###STT initialization ###
model_path = "vosk-model-small-en-us-0.15" #Vosk model path
model = vosk.Model(model_path) #inits model
recognizer = vosk.KaldiRecognizer(model, 16000) # open recognizer with model and sample rate
def listen(data):        #listens to mic and returns text
    if recognizer.AcceptWaveform(data):#if data is recognized
        result = recognizer.Result()#gets result from recognizer
        text = json.loads(result)["text"]#extracts text from result
        if text:
            print(text)
            return text
        print(None)
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
            try:

                text=transliteration.transliterate(text)
                engine.say(text)
                engine.runAndWait()
                
            except Exception as e:
                print(f"(TTS Error: {e})")
            finally:
                time.sleep(0.5)  # Short pause to prevent immediate self-listening
if __name__ == "__main__": #checks if the script is run directly
    while True:
        text = listen()
        if text:
            print("You said:", text)