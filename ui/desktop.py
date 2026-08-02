import asyncio
import sys
from config import config
from agents.orchestrator import run_orchestrator
from db.mongo import db_manager
from speech.tts import speak_text
from speech.stt import voice_listener

# Ensure UTF-8 output encoding if supported by terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

async def start_interactive_cli():
    """Interactive CLI supporting both Voice ('Hey Nova') and Keyboard input modes."""
    await db_manager.connect()
    
    print("\n" + "=" * 60)
    print(f"       NOVA - AI Operating System Assistant Ready")
    print("=" * 60)
    print("Modes available:")
    print("  [1] Keyboard Mode (Type your commands)")
    print("  [2] Continuous Voice Mode (Listen for 'Hey Nova')")
    print("  [3] Single Voice Command (Listen once)")
    print("Type 'exit' to quit.\n")

    mode = input("Select Mode (1, 2, or 3) [Default=1]: ").strip()

    if mode == "2":
        print(f"\n[VOICE MODE] Active! Say 'Hey Nova' to wake the assistant...")
        speak_text(f"{config.ASSISTANT_NAME} is active and listening for your wake word.")
        
        while True:
            try:
                # Listen for 'Hey Nova'
                triggered = voice_listener.listen_for_wake_word()
                if triggered:
                    speak_text("Yes, I am listening.")
                    command = voice_listener.listen_command()
                    if command:
                        response = await run_orchestrator(command)
                        explanation = response.get("explanation", "Task completed.")
                        print(f"[RESPONSE] {explanation}")
                        speak_text(explanation)
            except KeyboardInterrupt:
                print("\nExiting Voice Mode.")
                break
            except Exception as e:
                print(f"Voice listening error: {e}")
                await asyncio.sleep(1)

    elif mode == "3":
        speak_text("Listening for command...")
        command = voice_listener.listen_command()
        if command:
            response = await run_orchestrator(command)
            explanation = response.get("explanation", "Task completed.")
            print(f"\n[RESPONSE] {explanation}")
            speak_text(explanation)
        else:
            print("No voice command detected.")

    else:
        print("\n[KEYBOARD MODE] Active. Type your requests below:\n")
        initial_command = mode if mode and mode not in ["1", "keyboard"] else None
        
        while True:
            try:
                if initial_command:
                    user_input = initial_command
                    print(f"{config.ASSISTANT_NAME} > {user_input}")
                    initial_command = None
                else:
                    user_input = input(f"{config.ASSISTANT_NAME} > ").strip()

                if not user_input:
                    continue
                if user_input.lower() in ["exit", "quit", "q"]:
                    print(f"Shutting down {config.ASSISTANT_NAME}. Goodbye!")
                    break

                response = await run_orchestrator(user_input)
                
                explanation = response.get("explanation", "Task completed.")
                print(f"\n[AGENT CHOSEN] {response.get('target_agent', 'N/A').upper()}")
                print(f"[TOOL USED] {response.get('selected_tool')}")
                print(f"[EXPLANATION] {explanation}")
                print(f"[RESULT] {response.get('result')}\n")
                
                # Speak response aloud
                speak_text(explanation)
            except KeyboardInterrupt:
                print("\nExiting Assistant.")
                break
            except Exception as e:
                print(f"\n[ERROR] Processing command: {e}\n")
