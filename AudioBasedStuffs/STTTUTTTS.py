import AudioBasedStuffs.STT_TTS as STT_TTS
import SefariaAPIDispatchCommand
def STTTUTTTS(data):
    """Bridge the STT helper, Sefaria dispatch, and the TTS sink for a single audio chunk."""
    text=STT_TTS.listen(data)
    if text:
        print(text)
        text=SefariaAPIDispatchCommand.dispatch_command(text)
        print(text)
        STT_TTS.speak(text)
if __name__=='__main__':
    # Loop forever when running this module for manual testing.
    while True:
        STTTUTTTS()
