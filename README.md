# StudyBuddyAI

A voice-based study assistant that runs in the terminal and connects to an MCP (Model Context Protocol) server for all AI and tool interactions. The system aims to improve personalized learning experiences by dynamically adjusting flashcard difficulty, tracking weak topics, and providing feedback using a connected LLM.

## Documentation

- [Research Paper](https://www.overleaf.com/read/gpnszqrgppgr#b1dfb7)
- [Project Proposal Powerpoint](https://catmailohio-my.sharepoint.com/:p:/g/personal/cm787623_ohio_edu/EYlEPXB2uktJgjjnw2LK7r0BDT82YZ8N86R4CIziF-S67Q?e=ub1vKG)

## Installation

### Requirements

- [UV Python Package Manager](https://github.com/astral-sh/uv)
- [RealtimeSTT Installation Requirements](https://github.com/KoljaB/RealtimeSTT?tab=readme-ov-file#installation)

### Instructions

1. Clone the repository:

   ```bash
   git clone git@github.com:Colinster327/StudyBuddyAI.git
   ```

2. Change into the project directory:

   ```bash
   cd StudyBuddyAI
   ```

3. Create a virtual environment using Python 3.10:

   ```bash
   uv venv --python 3.10
   ```

4. Activate the virtual environment:

   ```bash
   # macOS
   source .venv/bin/activate

   # windows
   .venv\Scripts\activate
   ```

5. Install the dependencies:
   ```bash
   uv sync
   ```

You're now ready to use StudyBuddyAI!

## Usage

To start using StudyBuddyAI, simply run the main script:

```bash
uv run main.py

# or

python main.py
```

**How it works:**

1. When prompted, press Enter to start recording your voice.
2. Speak your question or task clearly into your microphone.
3. Press Enter again to stop recording.
4. StudyBuddyAI will transcribe your speech to text, send it to the AI, and display the assistant's response.

You can repeat the process to ask multiple questions.  
To exit the application at any time, press `Ctrl+C`.

**Tip:**  
If no speech is detected, you'll be prompted to try recording again.
