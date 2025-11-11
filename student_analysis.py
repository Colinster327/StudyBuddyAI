"""
Student Analysis and Response Evaluation

Functions for analyzing student responses and displaying metrics.
"""

from models import StudentModel, AdaptiveLearningPath
from typing import Optional
from openai import OpenAI


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


def evaluate_answer_with_llm(client: OpenAI, question: str, user_input: str, ai_response: str) -> Optional[bool]:
    """
    Use LLM to determine if the student's answer was correct.
    
    Returns:
        True if correct, False if incorrect, None if unable to determine
    """
    evaluation_prompt = f"""You are an educational assessment expert. Evaluate if the student's answer is correct.

Question/Context: {question}

Student's Answer: {user_input}

Tutor's Response: {ai_response}

Based on the question, student's answer, and the tutor's feedback, determine if the student answered correctly.

Respond with ONLY one word:
- "CORRECT" if the student's answer was right or mostly correct
- "INCORRECT" if the student's answer was wrong or showed misunderstanding
- "UNCLEAR" if you cannot determine from the context (e.g., not a question-answer interaction)"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",  # Using faster, cheaper model for evaluation
            messages=[
                {"role": "system", "content": "You are an educational assessment expert. Respond with only one word: CORRECT, INCORRECT, or UNCLEAR."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        if "CORRECT" in result and "INCORRECT" not in result:
            return True
        elif "INCORRECT" in result:
            return False
        else:
            return None
            
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: LLM evaluation failed: {e}{Colors.END}")
        return None


def analyze_student_response(question: str, user_input: str, ai_response: str, 
                            student_model: StudentModel, 
                            learning_path: Optional[AdaptiveLearningPath] = None,
                            client: Optional[OpenAI] = None):
    """Analyze student response to update cognitive model using LLM evaluation"""
    
    if not student_model:
        return
    
    is_correct = None
    
    # Primary method: Use LLM for accurate evaluation
    if client:
        is_correct = evaluate_answer_with_llm(client, question, user_input, ai_response)
    
    # Fallback: Simple heuristic analysis if LLM evaluation fails or is unavailable
    if is_correct is None:
        ai_lower = ai_response.lower()
        
        # Detect if the AI is providing correction or positive feedback
        positive_indicators = ["correct", "great", "excellent", "right", "exactly", "perfect", "well done"]
        negative_indicators = ["incorrect", "not quite", "actually", "mistake", "wrong", "let me clarify"]
        
        is_positive = any(indicator in ai_lower for indicator in positive_indicators)
        is_negative = any(indicator in ai_lower for indicator in negative_indicators)
        
        if is_positive and not is_negative:
            is_correct = True
        elif is_negative and not is_positive:
            is_correct = False
    
    # Update cognitive and affective models based on evaluation
    if is_correct is True:
        student_model.cognitive.update_knowledge(True, "general")
        student_model.affective.update_after_correct()
    elif is_correct is False:
        student_model.cognitive.update_knowledge(False, "general")
        student_model.affective.update_after_incorrect()
    
    # Update learning path if we have one
    if learning_path and is_correct is not None:
        learning_path.update_progress(is_correct)


def display_learning_metrics(student_model: StudentModel):
    """Display current learning metrics to the student"""
    if not student_model:
        return
    
    knowledge = student_model.cognitive.knowledge_level
    engagement = student_model.affective.engagement_level
    
    # Color code based on levels
    knowledge_color = Colors.GREEN if knowledge > 0.6 else (Colors.YELLOW if knowledge > 0.3 else Colors.RED)
    engagement_color = Colors.GREEN if engagement > 0.6 else (Colors.YELLOW if engagement > 0.4 else Colors.RED)
    
    print()
    print(f"{Colors.CYAN}📈 Learning Metrics:{Colors.END} ", end="")
    print(f"Knowledge: {knowledge_color}{knowledge:.0%}{Colors.END} | ", end="")
    print(f"Engagement: {engagement_color}{engagement:.0%}{Colors.END}")


def display_student_profile(student_model: StudentModel):
    """Display student profile summary at startup"""
    print(f"{Colors.CYAN}📊 Student Profile:{Colors.END}")
    print(f"   Knowledge Level: {student_model.cognitive.knowledge_level:.1%}")
    print(f"   Sessions: {student_model.session_count}")
    print(f"   Total Questions: {student_model.cognitive.total_answers}")
    if student_model.cognitive.mastered_topics:
        print(f"   Mastered: {', '.join(student_model.cognitive.mastered_topics[:3])}")
    print()

