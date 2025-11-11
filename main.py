"""
StudyBuddyAI - Advanced Personalized Learning System

This implementation integrates cutting-edge research from two papers on
Intelligent Tutoring Systems (ITS) to create a sophisticated, adaptive
learning experience.

RESEARCH FOUNDATION:
-------------------
Paper 1: "Empowering Personalized Learning through a Conversation-based 
         Tutoring System with Student Modeling" (CHI 2024)
         
Paper 2: "LLM-powered Multi-agent Framework for Goal-oriented Learning 
         in Intelligent Tutoring System (GenMentor)" (WWW 2025)

For complete documentation, see PERSONALIZED_LEARNING.md
"""

import logging
import warnings
import os
import json
from datetime import datetime
from typing import Optional

from RealtimeSTT import AudioToTextRecorder
from openai import OpenAI

# Import our modules
from models import StudentModel, AdaptiveLearningPath
from database import (
    init_database,
    load_student_profile,
    save_student_profile,
    save_session_history
)
from adaptive_learning import (
    generate_personalized_prompt,
    generate_session_summary,
    update_learning_style_from_interaction,
    map_goal_to_skills,
    update_skill_mastery
)
from student_analysis import (
    analyze_student_response,
    display_learning_metrics,
    display_student_profile
)


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
student_model: Optional[StudentModel] = None
learning_path: Optional[AdaptiveLearningPath] = None
session_start_time = None


# ============================================================================
# INITIALIZATION
# ============================================================================

def init():
    global recorder, client, messages, student_model, learning_path, session_start_time

    print()
    print(f"{Colors.BOLD}{Colors.BLUE}Initializing StudyBuddyAI with Personalized Learning...{Colors.END}")
    print()

    recorder = AudioToTextRecorder(
        level=logging.CRITICAL,
        no_log_file=True,
        spinner=False,
    )

    client = OpenAI()

    # Load flashcards
    flashcards_path = os.path.join(
        os.path.dirname(__file__), "os-flashcards.json")
    with open(flashcards_path, 'r') as f:
        flashcards = json.load(f)

    # Format flashcards for the system prompt
    flashcards_text = "# Study Material - Operating Systems Flashcards\n\n"
    for i, card in enumerate(flashcards, 1):
        flashcards_text += f"{i}. Q: {card['question']}\n"
        flashcards_text += f"   A: {card['answer']}\n\n"

    # ===== Initialize SQLite Database =====
    init_database()

    # ===== Initialize Student Model (Paper 1 & 2 Integration) =====
    student_model = load_student_profile("default")
    student_model.session_count += 1
    student_model.last_session = datetime.now().isoformat()

    # Initialize learning path (Paper 2: Adaptive Path Scheduling)
    learning_path = AdaptiveLearningPath(flashcards, student_model)

    # Map learning goals to skills (Paper 2: Goal-to-Skill Mapping)
    if not student_model.learning_goals:
        student_model.learning_goals = ["Pass Operating Systems Exam"]

    skills = map_goal_to_skills(student_model.learning_goals[0])
    update_skill_mastery(student_model, skills)

    # Display student profile summary
    display_student_profile(student_model)

    # Generate personalized system prompt (Paper 1: Adaptive Prompts)
    system_prompt = generate_personalized_prompt(
        student_model, flashcards_text)

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    session_start_time = datetime.now()


# ============================================================================
# VOICE INPUT
# ============================================================================

def record_text() -> tuple[str, float]:
    """Record text and return both text and time taken"""
    start_time = datetime.now()
    input("Press Enter to start recording...")
    recorder.start()
    input("Recording... (Press Enter to stop)")
    recorder.stop()

    text = recorder.text()
    time_taken = (datetime.now() - start_time).total_seconds()

    if not text or text.strip() == "":
        print(f"{Colors.RED}No speech detected. Please try again.{Colors.END}")
        print()
        return "", time_taken

    print()
    print(f"{Colors.CYAN}You:{Colors.END} {Colors.BOLD}'{text}'{Colors.END}")
    print()
    return text, time_taken


# ============================================================================
# AI INTERACTION
# ============================================================================

def ask_openai(prompt: str, first: bool = False, response_time: float = 0.0):
    """Enhanced ask_openai with student modeling integration"""
    global student_model

    if prompt.strip() == "" and not first:
        return

    if not first:
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Update engagement based on response (Paper 1: Affective Modeling)
        if student_model:
            student_model.affective.update_engagement(
                len(prompt), response_time)
            update_learning_style_from_interaction(student_model, prompt)

    content = []
    stream = client.chat.completions.create(
        model="gpt-5",
        reasoning_effort="minimal",
        messages=messages,
        stream=True
    )

    print(f"{Colors.GREEN}Study Buddy:{Colors.END}{Colors.BOLD}-------------------------{Colors.END}")
    print()
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            content.append(delta.content)
            print(f"{Colors.WHITE}{delta.content}{Colors.END}",
                  end="", flush=True)

    print()
    print()

    # Display real-time learning metrics (if significant interaction)
    if student_model and not first and student_model.cognitive.total_answers > 0:
        display_learning_metrics(student_model)

    print(f"{Colors.BOLD}---------------------------------------{Colors.END}")
    print()
    full_response = "".join(content)
    messages.append({
        "role": "assistant",
        "content": full_response
    })

    # Analyze response for performance indicators using LLM
    if student_model and not first:
        # messages[-3] is the previous AI turn (which may have asked a question)
        # messages[-2] is the user's input
        # messages[-1] is the current AI response
        previous_ai_content = messages[-3]["content"] if len(
            messages) >= 3 else ""
        analyze_student_response(
            previous_ai_content, prompt, full_response, student_model, learning_path, client)


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def generate_and_display_session_summary():
    """Generate session summary using AI (Paper 1: Feedback Loop)"""
    global student_model

    if not student_model or student_model.cognitive.total_answers == 0:
        return

    print()
    print(f"{Colors.BOLD}{Colors.CYAN}📋 Generating Session Summary...{Colors.END}")
    print()

    summary_prompt = generate_session_summary(student_model)

    # Ask AI to generate summary
    summary_messages = [
        {"role": "system", "content": "You are an educational assessment assistant. Provide concise, actionable feedback."},
        {"role": "user", "content": summary_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-5",
            reasoning_effort="minimal",
            messages=summary_messages
        )

        summary = response.choices[0].message.content
        print(f"{Colors.WHITE}{summary}{Colors.END}")
        print()

    except Exception as e:
        print(f"{Colors.YELLOW}Could not generate summary: {e}{Colors.END}")


def display_final_stats():
    """Display final session statistics and save to database"""
    global student_model, session_start_time

    if not student_model:
        return

    session_duration = (
        datetime.now() - session_start_time).total_seconds() / 60
    student_model.total_study_time += session_duration

    # Save session history to database
    save_session_history(
        student_model,
        session_duration,
        student_model.cognitive.total_answers,
        student_model.cognitive.correct_answers
    )

    print(f"{Colors.BOLD}{Colors.MAGENTA}📊 Session Statistics{Colors.END}")
    print(f"{Colors.CYAN}Duration:{Colors.END} {session_duration:.1f} minutes")
    print(f"{Colors.CYAN}Questions Answered:{Colors.END} {student_model.cognitive.total_answers}")
    print(f"{Colors.CYAN}Correct Answers:{Colors.END} {student_model.cognitive.correct_answers}")
    if student_model.cognitive.total_answers > 0:
        accuracy = student_model.cognitive.correct_answers / \
            student_model.cognitive.total_answers
        print(f"{Colors.CYAN}Session Accuracy:{Colors.END} {accuracy:.1%}")
    print(f"{Colors.CYAN}Overall Knowledge:{Colors.END} {student_model.cognitive.knowledge_level:.1%}")
    print(f"{Colors.CYAN}Total Study Time:{Colors.END} {student_model.total_study_time:.1f} minutes")
    print()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    global student_model

    print()
    print(f"{Colors.BOLD}{Colors.BLUE}---------------------------------------{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}StudyBuddyAI - Personalized AI Tutor{Colors.END}")
    print(f"{Colors.YELLOW}Press Ctrl+C to end session and save progress{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}---------------------------------------{Colors.END}")
    print()

    # Ask first question
    ask_openai("", first=True)

    while True:
        try:
            text, response_time = record_text()
            ask_openai(text, response_time=response_time)

        except KeyboardInterrupt:
            print()
            print()
            print(f"{Colors.BOLD}{Colors.GREEN}Ending Study Session...{Colors.END}")
            print()

            # Generate session summary (Paper 1: Feedback Loop)
            generate_and_display_session_summary()

            # Display final statistics
            display_final_stats()

            # Save student profile (Paper 1 & 2: Persistence)
            if student_model:
                save_student_profile(student_model)

            print()
            print(f"{Colors.GREEN}✓ Progress saved! See you next time!{Colors.END}")
            break


if __name__ == "__main__":
    init()
    main()
