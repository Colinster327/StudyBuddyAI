import logging
import warnings
import os

from RealtimeSTT import AudioToTextRecorder
from openai import OpenAI

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
        print("No speech detected. Please try again.")
        print()
        return ""

    print()
    print(f"You: '{text}'")
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
        messages=messages,
        stream=True
    )

    print("Expert Response:-----------------------")
    print()
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            content.append(delta.content)
            print(delta.content, end="", flush=True)

    print()
    print()
    print("---------------------------------------")
    print()
    full_response = "".join(content)
    messages.append({
        "role": "assistant",
        "content": full_response
    })


def main():
    print()
    print("---------------------------------------")
    print("StudyBuddyAI - Voice-Based, AI-Powered Study Assistant")
    print("Press Ctrl+C to stop the program")
    print("---------------------------------------")
    print()

    while True:
        try:
            text = record_text()
            ask_openai(text)

        except KeyboardInterrupt:
            print()
            print()
            print("Thank you for using StudyBuddyAI! Goodbye!")
            break


if __name__ == "__main__":
    init()
    main()
