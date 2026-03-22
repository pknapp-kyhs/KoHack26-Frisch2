import STT_TTS
import SefariaAPIDispatchCommand
def STTTUTTTS():
    text=STT_TTS.listen()
    if text:
        print(text)
        text=SefariaAPIDispatchCommand.dispatch_command(text)
        print(text)
        STT_TTS.speak(text)
if __name__=='__main__':
    while True:
        STTTUTTTS()