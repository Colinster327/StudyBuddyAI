"""
MCP Client Wrapper for StudyBuddyAI

Provides a simple interface for main.py to interact with the MCP server via stdin/stdout.
"""

import json
import subprocess
import sys
import os
import time
from typing import Any, Optional, Dict


class MCPClient:
    """Client wrapper for communicating with the StudyBuddyAI MCP server via stdin/stdout"""
    
    def __init__(self):
        """Initialize the MCP client and start the server process"""
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 0
        self._start_server()
    
    def _start_server(self):
        """Start the MCP server as a subprocess"""
        server_path = os.path.join(os.path.dirname(__file__), "studybuddy_server.py")
        
        # Start server process with stdin/stdout pipes
        self.process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give server a moment to start
        time.sleep(0.5)
        
        # Check if server crashed immediately
        poll_result = self.process.poll()
        if poll_result is not None:
            # Server has already exited - read stderr
            stderr_output = self.process.stderr.read() if self.process.stderr else ""
            raise Exception(f"MCP server failed to start. Exit code: {poll_result}\n\nServer error:\n{stderr_output}")
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "studybuddy-client",
                    "version": "0.1.0"
                }
            }
        }
        
        self._send_request(init_request)
        response = self._read_response()
        
        if response and "result" not in response:
            raise Exception(f"Failed to initialize MCP server: {response}")
        
        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        self._send_request(initialized_notif)
    
    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    def _send_request(self, request: Dict[str, Any]):
        """Send a JSON-RPC request to the server"""
        if not self.process or not self.process.stdin:
            raise Exception("MCP server process not running")
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()
    
    def _read_response(self) -> Optional[Dict[str, Any]]:
        """Read a JSON-RPC response from the server"""
        if not self.process or not self.process.stdout:
            raise Exception("MCP server process not running")
        
        line = self.process.stdout.readline()
        if not line:
            return None
        
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None
    
    def is_alive(self) -> bool:
        """Check if the MCP server process is still running"""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
        
        Returns:
            Parsed result from the tool call
        """
        # Check if server is still alive
        if not self.is_alive():
            return {"success": False, "error": "MCP server is not running"}
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            self._send_request(request)
            response = self._read_response()
            
            if not response:
                return {"success": False, "error": "No response from MCP server"}
            
            if "error" in response:
                return {"success": False, "error": f"MCP tool error: {response['error']}"}
            
            # Extract text content from response
            if "result" in response and "content" in response["result"]:
                content = response["result"]["content"]
                if content and len(content) > 0:
                    text = content[0].get("text", "{}")
                    return json.loads(text)
            
            return {"success": False, "error": "Invalid response format"}
        except (BrokenPipeError, OSError):
            return {"success": False, "error": "MCP server connection lost"}
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read an MCP resource.
        
        Args:
            uri: Resource URI (e.g., "student-profiles://list")
        
        Returns:
            Parsed resource content
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }
        
        try:
            self._send_request(request)
            response = self._read_response()
            
            if not response:
                return {"success": False, "error": "No response from MCP server"}
            
            if "error" in response:
                return {"success": False, "error": f"MCP resource error: {response['error']}"}
            
            # Extract resource content
            if "result" in response and "contents" in response["result"]:
                contents = response["result"]["contents"]
                if contents and len(contents) > 0:
                    text = contents[0].get("text", "{}")
                    return json.loads(text)
            
            return {"success": False, "error": "Invalid response format"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def close(self):
        """Close the MCP client and shutdown the server"""
        if self.process:
            try:
                if self.is_alive():
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except:
                pass  # Already dead, that's fine
            finally:
                self.process = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions for common operations
def create_student_profile(client: MCPClient, student_id: str = "default", 
                          learning_goals: Optional[list] = None) -> Dict[str, Any]:
    """Create or load a student profile"""
    args = {"student_id": student_id}
    if learning_goals:
        args["learning_goals"] = learning_goals
    return client.call_tool("create_student_profile", args)


def analyze_response(client: MCPClient, student_id: str, question: str, 
                     user_input: str, ai_response: str) -> Dict[str, Any]:
    """Analyze a student response"""
    return client.call_tool("analyze_student_response", {
        "student_id": student_id,
        "question": question,
        "user_input": user_input,
        "ai_response": ai_response
    })


def update_learning_metrics(client: MCPClient, student_id: str, 
                           response_text: str, response_time: float) -> Dict[str, Any]:
    """Update learning metrics based on interaction"""
    return client.call_tool("update_learning_metrics", {
        "student_id": student_id,
        "response_text": response_text,
        "response_time": response_time
    })


def generate_study_prompt(client: MCPClient, student_id: str, 
                         include_flashcards: bool = True) -> Dict[str, Any]:
    """Generate a personalized study prompt"""
    return client.call_tool("generate_study_prompt", {
        "student_id": student_id,
        "include_flashcards": include_flashcards
    })


def start_session(client: MCPClient, student_id: str) -> Dict[str, Any]:
    """Start a new study session"""
    return client.call_tool("start_session", {"student_id": student_id})


def save_session(client: MCPClient, student_id: str, duration_minutes: float,
                questions_answered: int, correct_answers: int) -> Dict[str, Any]:
    """Save session history"""
    return client.call_tool("save_session", {
        "student_id": student_id,
        "duration_minutes": duration_minutes,
        "questions_answered": questions_answered,
        "correct_answers": correct_answers
    })


def get_learning_metrics(client: MCPClient, student_id: str) -> Dict[str, Any]:
    """Get current learning metrics"""
    return client.call_tool("get_learning_metrics", {"student_id": student_id})


def save_student_profile(client: MCPClient, student_id: str) -> Dict[str, Any]:
    """Save student profile to database"""
    return client.call_tool("save_student_profile", {"student_id": student_id})
