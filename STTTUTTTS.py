import SpeechToText
import SefariaAPIDispatchCommand
import TTS
def STTTUTTTS():
    text=SpeechToText.listen()
    text=SefariaAPIDispatchCommand(text)
    TTS.speak(text)