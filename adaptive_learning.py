"""
Adaptive Learning System for StudyBuddyAI

Adaptive prompt generation, goal-to-skill mapping, and learning style inference.
"""

from typing import List
from models import StudentModel, Skill


def generate_personalized_prompt(student: StudentModel, flashcards_text: str) -> str:
    """Generate adaptive system prompt based on student model"""
    
    # Cognitive adaptations
    knowledge_descriptor = "beginner"
    if student.cognitive.knowledge_level > 0.7:
        knowledge_descriptor = "advanced"
    elif student.cognitive.knowledge_level > 0.4:
        knowledge_descriptor = "intermediate"
    
    # Affective adaptations
    motivation_note = ""
    if student.affective.motivation_level < 0.5:
        motivation_note = "\n- Provide extra encouragement and celebrate small wins to boost motivation"
    
    frustration_note = ""
    if student.affective.frustration_level > 0.6:
        frustration_note = "\n- Student may be frustrated - be patient, offer hints, and break down concepts into smaller steps"
    
    engagement_note = ""
    if student.affective.engagement_level < 0.5:
        engagement_note = "\n- Try to increase engagement with questions, examples, and interactive explanations"
    
    # Learning style adaptations
    styles = student.learning_style.get_dominant_style()
    style_instructions = ""
    
    if "active" in styles:
        style_instructions += "\n- This student learns by DOING - suggest practice problems and hands-on exercises"
    elif "reflective" in styles:
        style_instructions += "\n- This student learns by THINKING - give them time to reflect and ask probing questions"
    
    if "visual" in styles:
        style_instructions += "\n- This student prefers VISUAL learning - use diagrams, analogies, and descriptive examples when possible"
    elif "verbal" in styles:
        style_instructions += "\n- This student prefers VERBAL learning - use clear explanations and word-based descriptions"
    
    if "sequential" in styles:
        style_instructions += "\n- This student prefers STEP-BY-STEP learning - present concepts in logical order"
    elif "global" in styles:
        style_instructions += "\n- This student prefers BIG-PICTURE learning - start with overview and context before details"
    
    if "sensing" in styles:
        style_instructions += "\n- This student prefers CONCRETE examples - use real-world applications and practical examples"
    elif "intuitive" in styles:
        style_instructions += "\n- This student prefers ABSTRACT thinking - focus on concepts, theories, and underlying principles"
    
    # Progress summary
    progress_info = f"""
## Student Progress Summary
- Knowledge Level: {student.cognitive.knowledge_level:.1%} ({knowledge_descriptor})
- Questions Answered: {student.cognitive.total_answers} ({student.cognitive.correct_answers} correct)
- Mastered Topics: {', '.join(student.cognitive.mastered_topics) if student.cognitive.mastered_topics else 'None yet'}
- Struggling With: {', '.join(student.cognitive.struggling_topics) if student.cognitive.struggling_topics else 'None identified'}
- Session Count: {student.session_count}
- Motivation: {student.affective.motivation_level:.1%}
- Engagement: {student.affective.engagement_level:.1%}
"""
    
    # Build complete personalized prompt
    personalized_prompt = f"""{flashcards_text}

---

{progress_info}

---

## Your Role
You are a friendly and highly adaptive AI study buddy helping a student prepare for their Operating Systems exam.

## Personalization Instructions
Adapt your teaching to this specific student:

**Knowledge Level**: {knowledge_descriptor.upper()}
- Adjust explanation complexity to match their current level
- They have answered {student.cognitive.total_answers} questions with {student.cognitive.knowledge_level:.1%} accuracy

**Emotional State**:{motivation_note}{frustration_note}{engagement_note}

**Learning Style Preferences**:{style_instructions}

## Core Responsibilities
1. Help the student understand and memorize the flashcard material above
2. Answer questions about Operating Systems concepts in a clear, supportive way
3. Quiz the student on the material when they're ready (choose appropriate difficulty)
4. Explain concepts in different ways if they're struggling
5. Provide encouragement and positive reinforcement
6. Use the flashcard content as your primary reference material
7. Help connect different concepts together
8. Continuously assess understanding and adapt your approach

## Adaptive Teaching Guidelines
- If student answers correctly multiple times, increase difficulty and depth
- If student struggles, simplify explanations and provide more scaffolding
- Monitor engagement and adjust interaction style accordingly
- Provide constructive feedback that builds confidence

## Available Tools
You have access to tools that help you understand and track the student:

1. **analyze_student_response**: After the student answers a question, use this to evaluate correctness and update their profile
2. **get_learning_metrics**: Check the student's current knowledge, engagement, and progress
3. **get_student_profile**: Get detailed information about the student's learning style and preferences
4. **get_next_question**: Retrieve an adaptive question from the learning path
5. **update_learning_metrics**: Update engagement based on interaction patterns

**When to use tools:**
- After asking a question and getting an answer → use `analyze_student_response` to track progress
- When you want to check how the student is doing → use `get_learning_metrics`
- When choosing what to teach next → use `get_student_profile` to understand their needs
- When you want to quiz them → use `get_next_question` for adaptive difficulty

Be conversational, patient, and responsive to the student's unique learning needs. Use your tools intelligently to provide a truly adaptive learning experience."""
    
    return personalized_prompt


def generate_session_summary(student: StudentModel) -> str:
    """Generate AI summary prompt for the session"""
    summary_prompt = f"""Based on this study session, provide a brief analysis:

Student Performance:
- Total Questions: {student.cognitive.total_answers}
- Correct Answers: {student.cognitive.correct_answers}
- Current Knowledge Level: {student.cognitive.knowledge_level:.1%}
- Mastered: {', '.join(student.cognitive.mastered_topics) if student.cognitive.mastered_topics else 'None'}
- Struggling: {', '.join(student.cognitive.struggling_topics) if student.cognitive.struggling_topics else 'None'}

Engagement Metrics:
- Motivation: {student.affective.motivation_level:.1%}
- Engagement: {student.affective.engagement_level:.1%}
- Frustration: {student.affective.frustration_level:.1%}

Please provide:
1. Brief assessment of progress (2-3 sentences)
2. Recommended focus areas for next session
3. Suggested teaching approach adjustments

Keep it concise and actionable."""
    
    return summary_prompt


def update_learning_style_from_interaction(student: StudentModel, response_text: str):
    """Infer learning style preferences from student responses"""
    response_lower = response_text.lower()
    
    # Detect preference for examples (sensing) vs theory (intuitive)
    if any(word in response_lower for word in ["example", "practical", "real", "concrete"]):
        student.learning_style.sensing_intuitive = max(0.0, student.learning_style.sensing_intuitive - 0.05)
    elif any(word in response_lower for word in ["theory", "concept", "principle", "abstract"]):
        student.learning_style.sensing_intuitive = min(1.0, student.learning_style.sensing_intuitive + 0.05)
    
    # Detect preference for visual vs verbal
    if any(word in response_lower for word in ["diagram", "picture", "visual", "show me"]):
        student.learning_style.visual_verbal = max(0.0, student.learning_style.visual_verbal - 0.05)
    
    # Detect preference for sequential vs global
    if any(word in response_lower for word in ["step", "order", "first", "next", "sequence"]):
        student.learning_style.sequential_global = max(0.0, student.learning_style.sequential_global - 0.05)
    elif any(word in response_lower for word in ["overview", "big picture", "overall", "summary"]):
        student.learning_style.sequential_global = min(1.0, student.learning_style.sequential_global + 0.05)


def map_goal_to_skills(goal_description: str) -> List[Skill]:
    """Simple goal-to-skill mapping for OS exam preparation"""
    # In a full implementation, this would use an LLM with Chain-of-Thought reasoning
    # For now, we'll use predefined mappings
    
    os_skills = [
        Skill("Process Management", "Understanding processes, fork(), exec(), and process lifecycle", 0.6),
        Skill("System Calls", "Knowledge of system calls and user/kernel mode transitions", 0.5),
        Skill("File Systems", "File descriptors, I/O operations, and file management", 0.6),
        Skill("Signals & Interrupts", "Handling asynchronous events and interrupts", 0.7),
        Skill("Shell Operations", "Understanding shell execution, pipes, and redirection", 0.6),
        Skill("Memory Management", "Address space, heap, stack management", 0.7),
        Skill("Compilation Pipeline", "Understanding compilation, linking, and program execution", 0.5),
    ]
    
    return os_skills


def update_skill_mastery(student: StudentModel, skills: List[Skill]):
    """Update skill mastery levels based on student performance"""
    for skill in skills:
        # Simple mapping: knowledge level influences skill mastery
        skill.mastery_level = student.cognitive.knowledge_level

