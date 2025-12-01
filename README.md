# StudyBuddyAI

A voice-based, AI-powered study assistant featuring **advanced personalized learning** based on cutting-edge research in Intelligent Tutoring Systems.

## ✨ New: MCP-Based Modular Architecture

StudyBuddyAI now uses the **Model Context Protocol (MCP)** for a clean, modular architecture:

- **🏗️ MCP Server**: All business logic exposed via MCP tools and resources
- **📡 Client-Server**: Clean separation between UI and logic
- **🔧 Extensible**: Easy to add new tools and resources
- **🧪 Testable**: Components can be tested independently
- **🔌 Reusable**: Other applications can use the MCP server

**See [MCP_ARCHITECTURE.md](MCP_ARCHITECTURE.md) for complete technical details.**

## ✨ Research-Backed Personalized Learning

StudyBuddyAI implements advanced features from two leading research papers:

- **🧠 Student Modeling**: Tracks cognitive, affective, and learning style dimensions
- **🎯 Adaptive Prompts**: Dynamically adjusts teaching based on your profile
- **📈 Real-time Metrics**: Monitor knowledge and engagement levels
- **🔄 Session Summaries**: AI-generated feedback after each study session
- **💾 Progress Persistence**: SQLite database saves your learning profile between sessions
- **🎓 Goal-Oriented Learning**: Maps your goals to specific skills and creates adaptive paths
- **📊 Session History**: Tracks every session for trend analysis

**See [PERSONALIZED_LEARNING.md](PERSONALIZED_LEARNING.md) for complete details.**  
**See [SQLITE_DATABASE.md](SQLITE_DATABASE.md) for database documentation.**

## Overview

A terminal-based study assistant that provides personalized, adaptive tutoring experiences. The system dynamically adjusts to your learning style, tracks your progress across sessions, and provides intelligent feedback to optimize your studying.

Built with a **modern MCP architecture** that separates concerns and enables extensibility.

## Documentation

- [MCP Architecture](MCP_ARCHITECTURE.md) - Technical details on the MCP server and client
- [Personalized Learning](PERSONALIZED_LEARNING.md) - Research-backed adaptive learning
- [Database Documentation](SQLITE_DATABASE.md) - SQLite schema and operations
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

The MCP server will start automatically and handle all student modeling and adaptive learning logic.

**How it works:**

1. **First Run**: System creates your personalized student profile
2. **Profile Display**: See your knowledge level, session count, and mastered topics
3. **Voice Recording**: Press Enter to start/stop recording your questions
4. **AI Response**: Get personalized explanations adapted to your learning style
5. **Real-time Metrics**: See your knowledge and engagement levels after each interaction
6. **Session End**: Press `Ctrl+C` to get an AI-generated summary and save your progress

### What You'll See

**On Startup:**
```
📊 Student Profile:
   Knowledge Level: 65.0%
   Sessions: 3
   Total Questions: 15
   Mastered: Process Management, System Calls
```

**During Study:**
```
📈 Learning Metrics: Knowledge: 75% | Engagement: 80%
```

**On Exit:**
```
📋 Generating Session Summary...
[AI-powered analysis and recommendations]

📊 Session Statistics
Duration: 12.5 minutes
Questions Answered: 8
Session Accuracy: 75.0%
✓ Progress saved! See you next time!
```

**Tip:**  
- The AI adapts its teaching style to match your learning preferences
- Your progress is saved automatically when you exit with `Ctrl+C`
- Each session builds on previous ones for continuous improvement

## Data Storage

Your learning profile is stored in a local SQLite database:

**Location**: `studybuddy.db` (auto-created in the project directory)

**Contains**:
- Your complete student profile (cognitive, affective, learning style)
- Session history and performance trends
- Topic mastery and struggling areas
- Learning goals and progress

**Backup**:
```bash
# Simple file copy
cp studybuddy.db studybuddy_backup.db
```

**Reset**:
```bash
# Delete database to start fresh
rm studybuddy.db
```

**Migration from JSON** (if you have old `profile_*.json` files):
```bash
python migrate_json_to_sqlite.py
```

See [SQLITE_DATABASE.md](SQLITE_DATABASE.md) for complete database documentation.
