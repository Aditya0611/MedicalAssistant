import speech_recognition as sr
import io
import tempfile
import os
from pydub import AudioSegment

def transcribe_audio(audio_bytes):
    """
    Transcribes audio bytes to text using Google Web Speech API.
    Converts input bytes (WebM/MP4/etc) to WAV using pydub for compatibility.
    Returns: The transcribed text string, or None if failed.
    """
    if not audio_bytes:
        return None
        
    recognizer = sr.Recognizer()
    
    try:
        # 1. Use pydub to read the audio bytes and convert to WAV
        audio_stream = io.BytesIO(audio_bytes)
        try:
            audio_segment = AudioSegment.from_file(audio_stream)
        except Exception as e:
            print(f"DEBUG: Pydub could not read audio file: {e}")
            return None

        # 2. Export to a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
            audio_segment.export(temp_wav.name, format="wav")
            temp_filename = temp_wav.name
            
        # 3. Read the WAV file with SpeechRecognition
        try:
            with sr.AudioFile(temp_filename) as source:
                audio_data = recognizer.record(source)
                
            # Transcribe with language support for India
            text = recognizer.recognize_google(audio_data, language="en-IN")
            
            # Cleanup
            os.remove(temp_filename)
            return text
            
        except sr.UnknownValueError:
            if os.path.exists(temp_filename): os.remove(temp_filename)
            return None
        except Exception as e:
            print(f"DEBUG: Error during speech recognition: {e}")
            if os.path.exists(temp_filename): os.remove(temp_filename)
            return None

    except Exception as e:
        print(f"DEBUG: Error in transcription pipeline: {e}")
        if 'temp_filename' in locals() and os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass
        return None
