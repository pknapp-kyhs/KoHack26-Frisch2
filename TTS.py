import pyttsx3
import transliteration
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'daniel' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
def speak(text):
            try:
                text=transliteration.transliterate(text)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"(TTS Error: {e})")
if __name__=="__main__":
    test_word = "שָׁלוֹם"
    speak(test_word)
    print(test_word)

            