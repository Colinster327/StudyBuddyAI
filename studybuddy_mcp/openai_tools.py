"""
Convert MCP tools to OpenAI function calling format
"""

from typing import List, Dict, Any


def mcp_to_openai_tool(mcp_tool: dict) -> dict:
    """Convert an MCP tool definition to OpenAI tool format"""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool["name"],
            "description": mcp_tool["description"],
            "parameters": mcp_tool["inputSchema"]
        }
    }


def get_openai_tools_for_tutor() -> List[Dict[str, Any]]:
    """
    Get the subset of MCP tools that should be available to the AI tutor.
    
    The AI tutor should be able to:
    - Analyze student responses
    - Get learning metrics
    - Update learning style inferences
    - Check student profile information
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "analyze_student_response",
                "description": "Analyze the student's response to determine if it's correct, and update their cognitive and affective models accordingly. Use this after the student answers a question to track their progress.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "Student identifier (use 'default' for the current student)"
                        },
                        "question": {
                            "type": "string",
                            "description": "The question that was asked"
                        },
                        "user_input": {
                            "type": "string",
                            "description": "The student's response/answer"
                        },
                        "ai_response": {
                            "type": "string",
                            "description": "Your feedback/response to the student"
                        }
                    },
                    "required": ["student_id", "question", "user_input", "ai_response"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_learning_metrics",
                "description": "Get the student's current learning metrics including knowledge level, engagement, mastered topics, and struggling topics. Use this to understand how the student is doing.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "Student identifier (use 'default' for the current student)"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_learning_metrics",
                "description": "Update the student's engagement level and infer their learning style preferences based on their interaction patterns. Use this when you notice patterns in how the student learns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "Student identifier"
                        },
                        "response_text": {
                            "type": "string",
                            "description": "The student's response text to analyze for learning style cues"
                        },
                        "response_time": {
                            "type": "number",
                            "description": "Time taken to respond in seconds"
                        }
                    },
                    "required": ["student_id", "response_text", "response_time"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_student_profile",
                "description": "Get the complete student profile including their knowledge level, learning style preferences, mastered topics, and session history. Use this to better understand the student.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "Student identifier (use 'default' for the current student)"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_next_question",
                "description": "Get the next adaptive question from the learning path based on the student's performance. Use this when you want to quiz the student on appropriate material.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "Student identifier"
                        }
                    },
                    "required": ["student_id"]
                }
            }
        }
    ]


def should_display_tool_call(tool_name: str) -> bool:
    """Determine if a tool call should be displayed to the user"""
    # Don't display these routine tool calls
    hidden_tools = {"update_learning_metrics"}
    return tool_name not in hidden_tools

