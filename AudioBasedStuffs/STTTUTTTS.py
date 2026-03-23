# Import the speech-to-text and text-to-speech module
import AudioBasedStuffs.STT_TTS as STT_TTS
# Import the command processor that fetches text from Sefaria
import SefariaAPIDispatchCommand

# Main function that orchestrates the entire voice interaction
def STTTUTTTS(data):
    """Bridge the STT helper, Sefaria dispatch, and the TTS sink for a single audio chunk."""
    # Use speech-to-text to convert the user's voice input to text
    text=STT_TTS.listen(data)
    # Only proceed if we successfully heard something
    if text:
        # Print the recognized text for debugging
        print(text)
        # Process the command and get the response text from Sefaria
        text=SefariaAPIDispatchCommand.dispatch_command(text)
        # Print the response for debugging
        print(text)
        # Use text-to-speech to speak the response back to the user
        STT_TTS.speak(text)

# If this file is run directly (not imported), start the voice loop
if __name__=='__main__':
    # Loop forever when running this module for manual testing.
    # Loop forever, continuously listening for voice commands
    while True:
        STTTUTTTS()
