#!/usr/bin/env python3
"""
StudyBuddyAI MCP Server

Exposes student modeling, adaptive learning, and session management
functionality through the Model Context Protocol.
"""

import json
import sys
import os
import signal
from typing import Any, Optional

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource

from models import StudentModel, AdaptiveLearningPath
from database import (
    init_database,
    load_student_profile,
    save_student_profile,
    save_session_history,
    get_session_history
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
    evaluate_answer_with_llm
)
from openai import OpenAI

# Initialize database on server start
init_database()

# Global OpenAI client for AI-enabled tools
openai_client: Optional[OpenAI] = None

# Cache for loaded student models and learning paths
student_cache: dict[str, StudentModel] = {}
learning_path_cache: dict[str, AdaptiveLearningPath] = {}


def save_all_cached_profiles():
    """Save all cached student profiles to database before shutdown"""
    for student_id, student in student_cache.items():
        try:
            print(f"Saving profile {student_id} to database")
            save_student_profile(student)
        except Exception as e:
            print(f"Error saving profile {student_id}: {e}", file=sys.stderr)


def signal_handler(signum, frame):
    """Handle shutdown signals by saving cached profiles"""
    save_all_cached_profiles()
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination request


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client"""
    global openai_client
    if openai_client is None:
        openai_client = OpenAI()
    return openai_client


def load_flashcards() -> list[dict]:
    """Load flashcards from JSON file"""
    flashcards_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "os-flashcards.json"
    )
    with open(flashcards_path, 'r') as f:
        return json.load(f)


# Initialize MCP server
app = Server("studybuddy-server")


# ============================================================================
# TOOLS - Student Profile Management
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools"""
    return [
        Tool(
            name="create_student_profile",
            description="Create or load a student profile. Returns the complete student model with cognitive, affective, and learning style data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Unique identifier for the student (default: 'default')"
                    },
                    "learning_goals": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of learning goals"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_student_profile",
            description="Retrieve current student profile with all metrics and progress data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier (default: 'default')"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="update_student_profile",
            description="Update specific fields in a student profile and save to database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Fields to update (e.g., learning_goals, session_count, total_study_time)"
                    }
                },
                "required": ["student_id", "updates"]
            }
        ),
        Tool(
            name="save_student_profile",
            description="Save the current student profile to the database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    }
                },
                "required": ["student_id"]
            }
        ),
        
        # Analysis & AI Tools
        Tool(
            name="analyze_student_response",
            description="Analyze a student's response using AI, update their cognitive and affective models, and return evaluation results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "question": {
                        "type": "string",
                        "description": "The question or prompt that was asked"
                    },
                    "user_input": {
                        "type": "string",
                        "description": "The student's response"
                    },
                    "ai_response": {
                        "type": "string",
                        "description": "The AI tutor's response/feedback"
                    }
                },
                "required": ["student_id", "question", "user_input", "ai_response"]
            }
        ),
        Tool(
            name="evaluate_answer",
            description="Use AI to evaluate if a student's answer is correct without updating their profile. Returns: correct, incorrect, or unclear.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question asked"
                    },
                    "user_answer": {
                        "type": "string",
                        "description": "The student's answer"
                    },
                    "ai_feedback": {
                        "type": "string",
                        "description": "The AI's feedback on the answer"
                    }
                },
                "required": ["question", "user_answer", "ai_feedback"]
            }
        ),
        Tool(
            name="update_learning_metrics",
            description="Update engagement and learning style based on interaction patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "response_text": {
                        "type": "string",
                        "description": "The student's response text"
                    },
                    "response_time": {
                        "type": "number",
                        "description": "Time taken to respond in seconds"
                    }
                },
                "required": ["student_id", "response_text", "response_time"]
            }
        ),
        
        # Adaptive Learning Tools
        Tool(
            name="generate_study_prompt",
            description="Generate a personalized system prompt for the AI tutor based on the student's profile, knowledge level, learning style, and affective state.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "include_flashcards": {
                        "type": "boolean",
                        "description": "Whether to include flashcard content in the prompt (default: true)"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="initialize_learning_path",
            description="Initialize an adaptive learning path for a student based on their profile and learning goals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="get_next_question",
            description="Get the next adaptive question based on student performance and learning path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    }
                },
                "required": ["student_id"]
            }
        ),
        
        # Session Management
        Tool(
            name="start_session",
            description="Start a new study session for a student. Increments session count and updates timestamps.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="save_session",
            description="Save session history with performance metrics to the database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "duration_minutes": {
                        "type": "number",
                        "description": "Session duration in minutes"
                    },
                    "questions_answered": {
                        "type": "integer",
                        "description": "Number of questions answered"
                    },
                    "correct_answers": {
                        "type": "integer",
                        "description": "Number of correct answers"
                    }
                },
                "required": ["student_id", "duration_minutes", "questions_answered", "correct_answers"]
            }
        ),
        Tool(
            name="get_session_history",
            description="Retrieve recent session history for a student.",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of sessions to retrieve (default: 10)"
                    }
                },
                "required": ["student_id"]
            }
        ),
        Tool(
            name="get_learning_metrics",
            description="Get current learning metrics for display (knowledge level, engagement, etc.).",
            inputSchema={
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "Student identifier"
                    }
                },
                "required": ["student_id"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        # Student Profile Management Tools
        if name == "create_student_profile":
            student_id = arguments.get("student_id", "default")
            learning_goals = arguments.get("learning_goals", ["Pass Operating Systems Exam"])
            
            student = load_student_profile(student_id)
            if learning_goals:
                student.learning_goals = learning_goals
                
                # Map goals to skills
                skills = map_goal_to_skills(learning_goals[0])
                update_skill_mastery(student, skills)
            
            # Cache the student model
            student_cache[student_id] = student
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "student_id": student_id,
                    "profile": student.to_dict()
                }, indent=2)
            )]
        
        elif name == "get_student_profile":
            student_id = arguments.get("student_id", "default")
            
            # Check cache first
            if student_id in student_cache:
                student = student_cache[student_id]
            else:
                student = load_student_profile(student_id)
                student_cache[student_id] = student
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "profile": student.to_dict()
                }, indent=2)
            )]
        
        elif name == "update_student_profile":
            student_id = arguments["student_id"]
            updates = arguments["updates"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(student, key):
                    setattr(student, key, value)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Profile updated",
                    "updated_fields": list(updates.keys())
                }, indent=2)
            )]
        
        elif name == "save_student_profile":
            student_id = arguments["student_id"]
            
            if student_id not in student_cache:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": "Student profile not loaded in cache"
                    })
                )]
            
            student = student_cache[student_id]
            save_student_profile(student)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Profile saved to database"
                }, indent=2)
            )]
        
        # Analysis & AI Tools
        elif name == "analyze_student_response":
            student_id = arguments["student_id"]
            question = arguments["question"]
            user_input = arguments["user_input"]
            ai_response = arguments["ai_response"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            learning_path = learning_path_cache.get(student_id)
            client = get_openai_client()
            
            # Analyze response (this updates the student model)
            analyze_student_response(
                question, user_input, ai_response, 
                student, learning_path, client
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "knowledge_level": student.cognitive.knowledge_level,
                    "engagement_level": student.affective.engagement_level,
                    "total_answers": student.cognitive.total_answers,
                    "correct_answers": student.cognitive.correct_answers
                }, indent=2)
            )]
        
        elif name == "evaluate_answer":
            question = arguments["question"]
            user_answer = arguments["user_answer"]
            ai_feedback = arguments["ai_feedback"]
            
            client = get_openai_client()
            result = evaluate_answer_with_llm(client, question, user_answer, ai_feedback)
            
            evaluation = "unclear"
            if result is True:
                evaluation = "correct"
            elif result is False:
                evaluation = "incorrect"
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "evaluation": evaluation,
                    "is_correct": result
                }, indent=2)
            )]
        
        elif name == "update_learning_metrics":
            student_id = arguments["student_id"]
            response_text = arguments["response_text"]
            response_time = arguments["response_time"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            
            # Update engagement
            student.affective.update_engagement(len(response_text), response_time)
            
            # Infer learning style
            update_learning_style_from_interaction(student, response_text)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "engagement_level": student.affective.engagement_level,
                    "learning_style": {
                        "active_reflective": student.learning_style.active_reflective,
                        "sensing_intuitive": student.learning_style.sensing_intuitive,
                        "visual_verbal": student.learning_style.visual_verbal,
                        "sequential_global": student.learning_style.sequential_global
                    }
                }, indent=2)
            )]
        
        # Adaptive Learning Tools
        elif name == "generate_study_prompt":
            student_id = arguments["student_id"]
            include_flashcards = arguments.get("include_flashcards", True)
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            
            flashcards_text = ""
            if include_flashcards:
                flashcards = load_flashcards()
                flashcards_text = "# Study Material - Operating Systems Flashcards\n\n"
                for i, card in enumerate(flashcards, 1):
                    flashcards_text += f"{i}. Q: {card['question']}\n"
                    flashcards_text += f"   A: {card['answer']}\n\n"
            
            prompt = generate_personalized_prompt(student, flashcards_text)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "prompt": prompt
                }, indent=2)
            )]
        
        elif name == "initialize_learning_path":
            student_id = arguments["student_id"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            flashcards = load_flashcards()
            
            learning_path = AdaptiveLearningPath(flashcards, student)
            learning_path_cache[student_id] = learning_path
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Learning path initialized",
                    "total_nodes": len(learning_path.path),
                    "current_index": learning_path.current_node_index
                }, indent=2)
            )]
        
        elif name == "get_next_question":
            student_id = arguments["student_id"]
            
            if student_id not in learning_path_cache:
                # Initialize if not exists
                if student_id not in student_cache:
                    student_cache[student_id] = load_student_profile(student_id)
                
                student = student_cache[student_id]
                flashcards = load_flashcards()
                learning_path_cache[student_id] = AdaptiveLearningPath(flashcards, student)
            
            learning_path = learning_path_cache[student_id]
            question = learning_path.get_next_question()
            
            if question is None:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "has_question": False,
                        "message": "No more questions available"
                    })
                )]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "has_question": True,
                    "question": question
                }, indent=2)
            )]
        
        # Session Management Tools
        elif name == "start_session":
            student_id = arguments["student_id"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            from datetime import datetime
            
            student.session_count += 1
            student.last_session = datetime.now().isoformat()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "session_count": student.session_count,
                    "last_session": student.last_session
                }, indent=2)
            )]
        
        elif name == "save_session":
            student_id = arguments["student_id"]
            duration = arguments["duration_minutes"]
            questions = arguments["questions_answered"]
            correct = arguments["correct_answers"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            student.total_study_time += duration
            
            save_session_history(student, duration, questions, correct)
            save_student_profile(student)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "message": "Session saved",
                    "total_study_time": student.total_study_time
                }, indent=2)
            )]
        
        elif name == "get_session_history":
            student_id = arguments["student_id"]
            limit = arguments.get("limit", 10)
            
            history = get_session_history(student_id, limit)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "sessions": history
                }, indent=2)
            )]
        
        elif name == "get_learning_metrics":
            student_id = arguments["student_id"]
            
            if student_id not in student_cache:
                student_cache[student_id] = load_student_profile(student_id)
            
            student = student_cache[student_id]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "metrics": {
                        "knowledge_level": student.cognitive.knowledge_level,
                        "engagement_level": student.affective.engagement_level,
                        "motivation_level": student.affective.motivation_level,
                        "frustration_level": student.affective.frustration_level,
                        "total_answers": student.cognitive.total_answers,
                        "correct_answers": student.cognitive.correct_answers,
                        "accuracy": student.cognitive.correct_answers / max(student.cognitive.total_answers, 1),
                        "mastered_topics": student.cognitive.mastered_topics,
                        "struggling_topics": student.cognitive.struggling_topics
                    }
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Unknown tool: {name}"
                })
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e),
                "type": type(e).__name__
            })
        )]


# ============================================================================
# RESOURCES - Data Access
# ============================================================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="student-profiles://list",
            name="Student Profiles List",
            mimeType="application/json",
            description="List all student profile IDs in the database"
        ),
        Resource(
            uri="flashcards://all",
            name="All Flashcards",
            mimeType="application/json",
            description="Complete set of study flashcards"
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    
    try:
        # Convert URI to string if it's an AnyUrl object
        uri_str = str(uri) if not isinstance(uri, str) else uri
        
        if uri_str == "student-profiles://list":
            # Get all student IDs from database
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "studybuddy.db")
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, session_count, last_session FROM student_profiles")
            rows = cursor.fetchall()
            conn.close()
            
            profiles = [
                {
                    "student_id": row[0],
                    "session_count": row[1],
                    "last_session": row[2]
                }
                for row in rows
            ]
            
            return json.dumps({
                "success": True,
                "profiles": profiles
            }, indent=2)
        
        elif uri_str == "flashcards://all":
            flashcards = load_flashcards()
            return json.dumps({
                "success": True,
                "flashcards": flashcards,
                "count": len(flashcards)
            }, indent=2)
        
        elif uri_str.startswith("session-history://"):
            student_id = uri_str.replace("session-history://", "")
            history = get_session_history(student_id)
            return json.dumps({
                "success": True,
                "student_id": student_id,
                "sessions": history
            }, indent=2)
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown resource URI: {uri_str}"
            })
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        })


# ============================================================================
# SERVER STARTUP
# ============================================================================

async def main():
    """Run the MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

