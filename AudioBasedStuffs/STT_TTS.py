# Audio capture and speech synthesis helpers that glue Vosk and pyttsx3 together.
import pyttsx3
import AudioBasedStuffs.transliteration as transliteration
import vosk
import json
import time
# STT initialization: load the Vosk model and prepare the recognizer.
model_path = "vosk-model-small-en-us-0.15" #Vosk model path
model = vosk.Model(model_path) #inits model
recognizer = vosk.KaldiRecognizer(model, 16000) # open recognizer with model and sample rate
def listen(data):
    """Listen for a single chunk of audio and return the transcribed text if any."""
    if recognizer.AcceptWaveform(data):#if data is recognized
        result = recognizer.Result()#gets result from recognizer
        text = json.loads(result)["text"]#extracts text from result
        if text:
            print(text)
            return text
        print(None)
        return None

# TTS initialization: configure pyttsx3 voice engine.
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'josh' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 75)
engine.setProperty('volume', 1.0)
def speak(text):
    """Transliterate the output and speak it through the OSX style voice engine."""
    try:
        text=transliteration.transliterate(text)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"(TTS Error: {e})")
    finally:
        time.sleep(0.5)  # Short pause to prevent immediate self-listening
if __name__ == "__main__":  # Run a simple loop when executing the module directly.
    while True:
        text = listen()
        if text:
            print("You said:", text)
