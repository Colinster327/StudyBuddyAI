import logging
import warnings
import os

from RealtimeSTT import AudioToTextRecorder
from openai import OpenAI

# ANSI Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # Reset to default

# Suppress ALL warnings from the audio processing libraries
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Suppress ctranslate2 warnings at the environment level
os.environ["CTRANSLATE2_LOG_LEVEL"] = "ERROR"

# Specifically suppress ctranslate2 and faster_whisper warnings
logging.getLogger("ctranslate2").setLevel(logging.ERROR)
logging.getLogger("faster_whisper").setLevel(logging.ERROR)

# Global variables that will be initialized in main()
recorder = None
client = None
messages = []


def init():
    global recorder, client, messages

    recorder = AudioToTextRecorder(
        level=logging.CRITICAL,
        no_log_file=True,
        spinner=False,
    )

    client = OpenAI()
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can answer questions and help with tasks."
        }
    ]


def record_text() -> str:
    input("Press Enter to start recording...")
    recorder.start()
    input("Recording... (Press Enter to stop)")
    recorder.stop()

    text = recorder.text()
    if not text or text.strip() == "":
        print(f"{Colors.RED}No speech detected. Please try again.{Colors.END}")
        print()
        return ""

    print()
    print(f"{Colors.CYAN}You:{Colors.END} {Colors.BOLD}'{text}'{Colors.END}")
    print()
    return text


def ask_openai(prompt: str):
    if prompt.strip() == "":
        return

    messages.append({
        "role": "user",
        "content": prompt
    })
    content = []
    stream = client.chat.completions.create(
        model="gpt-5",
        reasoning_effort="minimal",
        messages=messages,
        stream=True
    )

    print(f"{Colors.GREEN}Expert Response:{Colors.END}{Colors.BOLD}-----------------------{Colors.END}")
    print()
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            content.append(delta.content)
            print(f"{Colors.WHITE}{delta.content}{Colors.END}", end="", flush=True)

    print()
    print()
    print(f"{Colors.BOLD}---------------------------------------{Colors.END}")
    print()
    full_response = "".join(content)
    messages.append({
        "role": "assistant",
        "content": full_response
    })


def main():
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}---------------------------------------{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}StudyBuddyAI - Voice-Based, AI-Powered Study Assistant{Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop the program{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}---------------------------------------{Colors.END}")
    print()

    while True:
        try:
            text = record_text()
            ask_openai(text)

        except KeyboardInterrupt:
            print()
            print()
            print(f"{Colors.GREEN}Thank you for using StudyBuddyAI! Goodbye!{Colors.END}")
            break


if __name__ == "__main__":
    init()
    main()
