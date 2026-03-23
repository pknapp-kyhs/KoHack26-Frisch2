### All comments done by built in github copilot for the benefit of the teammates ###
import pyttsx3
import AudioBasedStuffs.transliteration as transliteration
import vosk
import threading
import time
import json
###STT initialization ###
model_path = "vosk-model-small-en-us-0.15" #Vosk model path
model = vosk.Model(model_path) #inits model

def create_recognizer():
    """Create a new per-client recognizer instance to avoid thread conflicts"""
    return vosk.KaldiRecognizer(model, 16000)

def listen(recognizer, data):        #listens to mic and returns text
    """Process audio chunk with given recognizer instance"""
    try:
        if recognizer.AcceptWaveform(data):#if data is recognized
            result = recognizer.Result()#gets result from recognizer
            # Use .get() so a silent/noise chunk with no lattice path returns "" instead of raising KeyError
            text = json.loads(result).get("text", "")
            if text:
                print(f"[STT] Recognized: {text}")
                return text
            return None
        else:
            # Return partial result if available
            partial_result = recognizer.PartialResult()
            if partial_result:
                partial_json = json.loads(partial_result)
                partial_text = partial_json.get("partial", "")
                if partial_text:
                    return partial_text
        return None
    except Exception as e:
        print(f"[STT Error] {e}")
        # Reset the recognizer so it can recover from a broken lattice state
        recognizer.Reset()
        return None

### TTS initialization ###
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'josh' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 75)
engine.setProperty('volume', 1.0)
def speak(text):
        """Speak text using TTS (async in separate thread)"""
        def run(text):
            try:
                text=transliteration.transliterate(text)
                engine.say(text)
                engine.runAndWait()
                print(f"[TTS] Speaking: {text}")
            except Exception as e:
                print(f"(TTS Error: {e})")
        
            finally:
                time.sleep(0.5)  # Short pause to prevent immediate self-listening
        threading.Thread(target=run,args=(text,), daemon=True).start()
