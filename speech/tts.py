import logging
import pyttsx3

logger = logging.getLogger(__name__)

def speak_text(text: str):
    """Synthesize speech using system TTS engine."""
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)  # Speed rate
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.warning(f"TTS voice synthesis warning: {e}")
