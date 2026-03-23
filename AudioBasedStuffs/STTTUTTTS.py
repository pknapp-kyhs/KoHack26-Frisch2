import AudioBasedStuffs.STT_TTS as STT_TTS
import SefariaAPIDispatchCommand
def STTTUTTTS(data):
    text=STT_TTS.listen(data)
    if text:
        print(text)
        text=SefariaAPIDispatchCommand.dispatch_command(text)
        print(text)
        STT_TTS.speak(text)
if __name__=='__main__':
    while True:
        STTTUTTTS()