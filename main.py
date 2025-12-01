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
import sys
from datetime import datetime
from typing import Optional

from RealtimeSTT import AudioToTextRecorder
from openai import OpenAI

# Import MCP client for modular architecture
from studybuddy_mcp.client import (
    MCPClient,
    create_student_profile,
    generate_study_prompt,
    start_session,
    save_session,
    get_learning_metrics,
    save_student_profile as mcp_save_profile
)
from studybuddy_mcp.openai_tools import (
    get_openai_tools_for_tutor,
    should_display_tool_call
)
import json

# Import database functions for direct access
from database import load_student_profile, save_student_profile, save_session_history


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
mcp_client: Optional[MCPClient] = None
student_id = "default"
session_start_time = None


# ============================================================================
# INITIALIZATION
# ============================================================================

def init():
    global recorder, client, messages, mcp_client, student_id, session_start_time

    print()
    print(f"{Colors.BOLD}{Colors.BLUE}Initializing StudyBuddyAI with Personalized Learning...{Colors.END}")
    print()

    recorder = AudioToTextRecorder(
        level=logging.CRITICAL,
        no_log_file=True,
        spinner=False,
    )

    client = OpenAI()

    # ===== Initialize MCP Client =====
    print(f"{Colors.CYAN}Starting MCP server...{Colors.END}")
    mcp_client = MCPClient()
    
    # ===== Create/Load Student Profile via MCP =====
    result = create_student_profile(
        mcp_client, 
        student_id=student_id,
        learning_goals=["Pass Operating Systems Exam"]
    )
    
    if not result.get("success"):
        print(f"{Colors.RED}Error initializing profile: {result.get('error')}{Colors.END}")
        print()
        sys.exit(1)
    
    profile = result.get("profile", {})
    
    # ===== Start New Session via MCP =====
    session_result = start_session(mcp_client, student_id)
    
    # ===== Initialize Learning Path via MCP =====
    mcp_client.call_tool("initialize_learning_path", {"student_id": student_id})
    
    # Display student profile summary
    display_student_profile_from_dict(profile)

    # ===== Generate Personalized System Prompt via MCP =====
    prompt_result = generate_study_prompt(mcp_client, student_id, include_flashcards=True)
    
    if not prompt_result.get("success"):
        print(f"{Colors.RED}Error generating prompt: {prompt_result.get('error')}{Colors.END}")
        return
    
    system_prompt = prompt_result.get("prompt", "")

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    session_start_time = datetime.now()
    print(f"{Colors.GREEN}✓ MCP initialization complete{Colors.END}")
    print()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def display_student_profile_from_dict(profile: dict):
    """Display student profile summary from profile dictionary"""
    cognitive = profile.get("cognitive", {})
    print(f"{Colors.CYAN}📊 Student Profile:{Colors.END}")
    print(f"   Knowledge Level: {cognitive.get('knowledge_level', 0):.1%}")
    print(f"   Sessions: {profile.get('session_count', 0)}")
    print(f"   Total Questions: {cognitive.get('total_answers', 0)}")
    mastered = cognitive.get('mastered_topics', [])
    if mastered:
        print(f"   Mastered: {', '.join(mastered[:3])}")
    print()


def display_learning_metrics_from_dict(metrics: dict):
    """Display learning metrics from metrics dictionary"""
    knowledge = metrics.get('knowledge_level', 0)
    engagement = metrics.get('engagement_level', 0)
    
    # Color code based on levels
    knowledge_color = Colors.GREEN if knowledge > 0.6 else (Colors.YELLOW if knowledge > 0.3 else Colors.RED)
    engagement_color = Colors.GREEN if engagement > 0.6 else (Colors.YELLOW if engagement > 0.4 else Colors.RED)
    
    print()
    print(f"{Colors.CYAN}📈 Learning Metrics:{Colors.END} ", end="")
    print(f"Knowledge: {knowledge_color}{knowledge:.0%}{Colors.END} | ", end="")
    print(f"Engagement: {engagement_color}{engagement:.0%}{Colors.END}")


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

def handle_tool_calls(tool_calls, mcp_client, student_id):
    """Handle tool calls from OpenAI by executing corresponding MCP tools"""
    tool_results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        
        # Display tool call if appropriate
        if should_display_tool_call(tool_name):
            print(f"{Colors.CYAN}🔧 Using tool: {tool_name}{Colors.END}")
        
        # Execute the MCP tool
        try:
            result = mcp_client.call_tool(tool_name, tool_args)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result)
            })
        except Exception as e:
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps({"success": False, "error": str(e)})
            })
    
    return tool_results


def ask_openai(prompt: str, first: bool = False, response_time: float = 0.0):
    """Enhanced ask_openai with student modeling integration via MCP tools"""
    global mcp_client, student_id

    if prompt.strip() == "" and not first:
        return

    if not first:
        messages.append({
            "role": "user",
            "content": prompt
        })

    # Get MCP tools for OpenAI
    tools = get_openai_tools_for_tutor()
    
    # Call OpenAI with tools - allow multiple rounds of tool calling
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Non-streaming call to handle tool calls properly
        response = client.chat.completions.create(
            model="gpt-5",
            reasoning_effort="minimal",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to call tools
        if response_message.tool_calls:
            # Add assistant's message with tool calls
            messages.append(response_message)
            
            # Execute tool calls via MCP
            tool_results = handle_tool_calls(
                response_message.tool_calls,
                mcp_client,
                student_id
            )
            
            # Add tool results to messages
            messages.extend(tool_results)
            
            # Continue loop to get final response
            continue
        else:
            # No more tool calls - display final response
            content = response_message.content or ""
            
            print(f"{Colors.GREEN}Study Buddy:{Colors.END}{Colors.BOLD}-------------------------{Colors.END}")
            print()
            print(f"{Colors.WHITE}{content}{Colors.END}")
            print()
            print()
            
            # Add final response to messages
            messages.append({
                "role": "assistant",
                "content": content
            })
            
            # Display learning metrics if available and not first message
            if not first:
                metrics_result = get_learning_metrics(mcp_client, student_id)
                if metrics_result.get("success"):
                    metrics = metrics_result.get("metrics", {})
                    if metrics.get("total_answers", 0) > 0:
                        display_learning_metrics_from_dict(metrics)
            
            print(f"{Colors.BOLD}---------------------------------------{Colors.END}")
            print()
            break


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def generate_and_display_session_summary():
    """Generate session summary using AI directly - no MCP dependency (Paper 1: Feedback Loop)"""
    global client, messages
    
    # Count interactions from conversation history
    # Skip system message, count user/assistant pairs
    interaction_count = sum(1 for msg in messages if msg["role"] == "user")
    
    if interaction_count == 0:
        return

    print()
    print(f"{Colors.BOLD}{Colors.CYAN}📋 Generating Session Summary...{Colors.END}")
    print()

    # Generate summary based on conversation history
    summary_prompt = f"""Based on this study session conversation, provide a brief analysis:

Conversation History:
{len(messages)} messages exchanged
{interaction_count} student interactions

Please provide:
1. Brief assessment of the student's engagement and progress (2-3 sentences)
2. Recommended focus areas for next session
3. One teaching tip based on observed learning patterns

Keep it concise and actionable."""

    try:
        # Call OpenAI directly (not through MCP)
        response = client.chat.completions.create(
            model="gpt-5",
            reasoning_effort="minimal",
            messages=[
                {"role": "system", "content": "You are an educational assessment assistant. Provide concise, actionable feedback based on the conversation history provided."},
                {"role": "user", "content": summary_prompt}
            ]
        )

        summary = response.choices[0].message.content
        print(f"{Colors.WHITE}{summary}{Colors.END}")
        print()

    except Exception as e:
        print(f"{Colors.YELLOW}Could not generate summary: {e}{Colors.END}")


def display_final_stats():
    """Display final session statistics and save to database directly"""
    global student_id, session_start_time

    if not session_start_time:
        return

    try:
        # Load student profile directly from database
        student_profile = load_student_profile(student_id)
        
        # Calculate session duration
        session_duration = (datetime.now() - session_start_time).total_seconds() / 60
        
        # Get cognitive metrics
        cognitive = student_profile.cognitive
        questions_answered = cognitive.total_answers
        correct_answers = cognitive.correct_answers
        knowledge_level = cognitive.knowledge_level
        
        # Calculate session accuracy
        accuracy = correct_answers / max(questions_answered, 1) if questions_answered > 0 else 0
        
        # Update and save student profile
        student_profile.total_study_time += session_duration
        student_profile.last_session = datetime.now().isoformat()
        save_student_profile(student_profile)
        
        # Save session history
        save_session_history(
            student_profile,
            duration=session_duration,
            questions=questions_answered,
            correct=correct_answers
        )

        # Display statistics
        print(f"{Colors.BOLD}{Colors.MAGENTA}📊 Session Statistics{Colors.END}")
        print(f"{Colors.CYAN}Duration:{Colors.END} {session_duration:.1f} minutes")
        print(f"{Colors.CYAN}Questions Answered:{Colors.END} {questions_answered}")
        print(f"{Colors.CYAN}Correct Answers:{Colors.END} {correct_answers}")
        if questions_answered > 0:
            print(f"{Colors.CYAN}Session Accuracy:{Colors.END} {accuracy:.1%}")
        print(f"{Colors.CYAN}Overall Knowledge:{Colors.END} {knowledge_level:.1%}")
        print(f"{Colors.CYAN}Total Study Time:{Colors.END} {student_profile.total_study_time:.1f} minutes")
        print()
    
    except Exception as e:
        # Show minimal stats if database is unavailable
        print(f"{Colors.BOLD}{Colors.MAGENTA}📊 Session Statistics{Colors.END}")
        session_duration = (datetime.now() - session_start_time).total_seconds() / 60
        print(f"{Colors.CYAN}Duration:{Colors.END} {session_duration:.1f} minutes")
        print(f"{Colors.YELLOW}(Error loading detailed stats: {e}){Colors.END}")
        print()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    global mcp_client, student_id

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

            print()
            break


if __name__ == "__main__":
    init()
    main()
