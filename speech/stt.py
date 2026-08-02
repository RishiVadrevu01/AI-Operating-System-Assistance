import logging
import sys
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Ensure UTF-8 output encoding if supported by terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class VoiceListener:
    """Voice listener supporting wake word detection and speech-to-text transcription."""
    
    def __init__(self, wake_word: str = "nova"):
        self.wake_word = wake_word.lower()
        self.recognizer = None
        self.microphone = None
        self.is_available = False
        self._init_speech_engine()

    def _init_speech_engine(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            # Dynamic energy threshold for sensitive microphone pickup
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.microphone = sr.Microphone()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            
            self.is_available = True
            print("[SUCCESS] Microphones & Audio Engine successfully connected!")
        except Exception as e:
            self.is_available = False
            print(f"[WARNING] Voice engine notice: {e}. Ensure PyAudio and a working microphone are present.")

    def listen_for_wake_word(self, timeout: Optional[int] = 5) -> bool:
        """Listen continuously for the wake word ('Hey Nova')."""
        if not self.is_available or not self.recognizer or not self.microphone:
            print("[ERROR] Microphone hardware or PyAudio not detected.")
            return False

        import speech_recognition as sr

        try:
            with self.microphone as source:
                print("[LISTENING] Listening for 'Hey Nova'...", end="\r", flush=True)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=4)
                text = self.recognizer.recognize_google(audio).lower().strip()
                print(f"\n[AUDIO HEARD] '{text}'")
                
                if any(w in text for w in ["nova", "hey nova", "hi nova", "hello nova", "no va"]):
                    print("\n[WAKE WORD DETECTED] 'Hey Nova' triggered!")
                    return True
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            logger.debug(f"Wake word listening error: {e}")

        return False

    def listen_command(self) -> Optional[str]:
        """Capture a spoken command from the microphone and transcribe it to text."""
        if not self.is_available or not self.recognizer or not self.microphone:
            print("[ERROR] Microphone hardware not ready.")
            return None

        import speech_recognition as sr
        print("\n[LISTENING COMMAND] Speak your command now!")

        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=10)
                print("[PROCESSING] Transcribing voice input...")
                command = self.recognizer.recognize_google(audio)
                print(f"[TRANSCRIBED COMMAND] '{command}'")
                return command
        except sr.UnknownValueError:
            print("[NOTICE] Could not understand audio clearly. Speak closer to your microphone.")
        except sr.RequestError as e:
            print(f"[ERROR] Speech Recognition API Error: {e}")
        except Exception as e:
            print(f"[ERROR] Microphone Listening Error: {e}")

        return None

voice_listener = VoiceListener()
