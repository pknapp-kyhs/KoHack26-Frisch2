# Import the speech-to-text and text-to-speech module
import AudioBasedStuffs.STT_TTS as STT_TTS
# Import the command processor that fetches text from Sefaria
import SefariaAPIDispatchCommand

class AudioEngine:
    """Engine for processing audio chunks from web and returning responses"""
    def __init__(self):
        # Create per-client recognizer to avoid thread conflicts
        self.recognizer = STT_TTS.create_recognizer()
    
    def process_chunk(self, audio_data):
        """Process audio chunk and return (status, text) tuple
        status can be: 'partial' (intermediate result), 'final' (complete utterance), or None
        """
        try:
            status, text = STT_TTS.listen(self.recognizer, audio_data)
            return (status, text)
        except Exception as e:
            print(f"[AudioEngine Error] {e}")
            return (None, "")

def create_engine():
    """Factory function to create a new AudioEngine instance"""
    return AudioEngine()

def handle_command(text):
    """Process recognized text and return response"""
    if not text:
        return None
    
    print(f"[Command] Processing: {text}")
    
    try:
        response_text = SefariaAPIDispatchCommand.dispatch_command(text)
        print(f"[Response] {response_text}")
        
        # Speak the response
        if response_text:
            STT_TTS.speak(response_text)
        
        return response_text
    except Exception as e:
        print(f"[Error] Failed to process command: {e}")
        return None