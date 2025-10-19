# StudyBuddyAI

A voice-based study assistant that runs in the terminal and connects to an MCP (Model Context Protocol) server for all AI and tool interactions. The system aims to improve personalized learning experiences by dynamically adjusting flashcard difficulty, tracking weak topics, and providing feedback using a connected LLM.

## Documentation

- [Research Paper](https://www.overleaf.com/read/gpnszqrgppgr#b1dfb7)
- [Project Proposal Powerpoint](https://catmailohio-my.sharepoint.com/:p:/g/personal/cm787623_ohio_edu/EYlEPXB2uktJgjjnw2LK7r0BDT82YZ8N86R4CIziF-S67Q?e=ub1vKG)

## Installation

### Requirements

- [UV Python Package Manager](https://github.com/astral-sh/uv)

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
