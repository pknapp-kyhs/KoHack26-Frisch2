### All comments done by built in github copilot for the benefit of the teammates ###
import pyttsx3
import transliteration
import vosk
import pyaudio
import json
###STT initialization ###
model_path = "vosk-model-small-en-us-0.15" #Vosk model path
model = vosk.Model(model_path) #inits model
recognizer = vosk.KaldiRecognizer(model, 16000) # open recognizer with model and sample rate
p = pyaudio.PyAudio() #inits pyaudio
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)#opens stream with format, channels, rate, input and frames per buffer
stream.start_stream()#starts the stream
def listen():        #listens to mic and returns text
    data = stream.read(4000, exception_on_overflow=False)#reads data from mic
    if recognizer.AcceptWaveform(data):#if data is recognized
        result = recognizer.Result()#gets result from recognizer
        text = json.loads(result)["text"]#extracts text from result
        if text:
            return text
        return None
### TTS initialization ###
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'daniel' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 75)
engine.setProperty('volume', 1.0)
def speak(text):
            try:
                if stream:
                    stream.stop_stream()
                text=transliteration.transliterate(text)
                engine.say(text)
                engine.runAndWait()
                if stream:
                    stream.start_stream()
            except Exception as e:
                print(f"(TTS Error: {e})")
if __name__ == "__main__": #checks if the script is run directly
    while True:
        text = listen()
        if text:
            print("You said:", text)