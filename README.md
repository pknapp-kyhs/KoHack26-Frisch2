# KoHack26-Frisch2

## Project Links
- Design / planning doc: https://docs.google.com/document/d/1dYoY_l0aqIEFUWol7nMtQwb--mUQhJSFkPwFrZQe-eY/edit?tab=t.0
- Code presentation: https://www.canva.com/design/DAHEsGMY4_c/fY-WQ-l1l3laV_3x-B_-IQ/edit?utm_content=DAHEsGMY4_c&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Files Involved
### Core Code
- `app.py` - Main Flask application that defines the routes, session login, Braille conversion, Sefaria prayer loading, and Socket.IO audio handling.
- `AudioBasedStuffs/STTTUTTTS.py` - Audio bridge that passes speech input into Sefaria command dispatch and text-to-speech output.
- `AudioBasedStuffs/STT_TTS.py` - Loads the Vosk model, listens for speech, and speaks translated text with `pyttsx3`.
- `AudioBasedStuffs/transliteration.py` - Hebrew transliteration helper that maps letters and niqqud into English phonetics.
- `SefariaAPIDispatchCommand.py` - Normalizes spoken references and turns them into Sefaria API requests.
- `sefaria_api.py` - Sends the Sefaria request and cleans the returned Hebrew and English text.
- `validate_passwd.py` - Checks whether a signup password meets the app's complexity rules.
- `templates/base.html` - Shared layout with the dyslexia-font toggle and common styling.
- `templates/audio.html` - Voice-search page that streams microphone audio to the backend.
- `templates/texts.html` - Braille conversion page for typed text and uploaded files.
- `templates/tefilla.html` - Prayer reader page that loads Sefaria text and shows transliteration.
- `templates/dashboard.html` - Logged-in landing page with links to the app's main tools.
- `templates/index.html` - Public landing page with sign-in and sign-up links.
- `templates/signin.html` - Sign-in form for existing users.
- `templates/signup.html` - Account creation form with password requirements.
- `templates/admin.html` - Simple admin page that lists current users and lets you remove them.
- `templates/openVoiceLine.html` - Legacy Socket.IO demo page for voice streaming.

### Supporting Assets
- `vosk-model-small-en-us-0.15/` - Local Vosk speech-recognition model files used by the audio pipeline.
- `static/fonts/opendyslexic/` - OpenDyslexic font files used when dyslexia mode is enabled.

## Three Features
1. Voice search and audio playback - the code is stored in `templates/audio.html`, `app.py`, `AudioBasedStuffs/STTTUTTTS.py`, `AudioBasedStuffs/STT_TTS.py`, `SefariaAPIDispatchCommand.py`, and `sefaria_api.py`.
2. Braille source sheets - the code is stored in `templates/texts.html` and the Braille helper functions inside `app.py`.
3. Tefilla reader - the code is stored in `templates/tefilla.html`, the Sefaria helper functions in `app.py`, and the transliteration support in `AudioBasedStuffs/transliteration.py`.
