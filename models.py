"""
Data Models for StudyBuddyAI

All dataclasses for student modeling, learning paths, and skill tracking.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
from enum import Enum


class LearningStyle(Enum):
    """Felder-Silverman Learning Style Model dimensions"""
    ACTIVE = "active"  # Learn by doing
    REFLECTIVE = "reflective"  # Learn by thinking
    SENSING = "sensing"  # Concrete, practical
    INTUITIVE = "intuitive"  # Abstract, theoretical
    VISUAL = "visual"  # Learn through images/diagrams
    VERBAL = "verbal"  # Learn through words/explanations
    SEQUENTIAL = "sequential"  # Step-by-step learning
    GLOBAL = "global"  # Big-picture learning


@dataclass
class CognitiveModel:
    """Cognitive dimensions of student learning"""
    knowledge_level: float = 0.5  # 0-1 scale, estimated competency
    metacognition_score: float = 0.5  # Self-awareness of learning
    attention_span: float = 0.7  # Engagement duration
    correct_answers: int = 0
    total_answers: int = 0
    mastered_topics: List[str] = field(default_factory=list)
    struggling_topics: List[str] = field(default_factory=list)
    
    def update_knowledge(self, correct: bool, topic: str):
        """Update knowledge level based on performance"""
        self.total_answers += 1
        if correct:
            self.correct_answers += 1
            if topic not in self.mastered_topics and self.get_topic_accuracy(topic) > 0.75:
                self.mastered_topics.append(topic)
        else:
            if topic not in self.struggling_topics:
                self.struggling_topics.append(topic)
        
        # Update overall knowledge level using moving average
        accuracy = self.correct_answers / max(self.total_answers, 1)
        self.knowledge_level = 0.7 * self.knowledge_level + 0.3 * accuracy
    
    def get_topic_accuracy(self, topic: str) -> float:
        """Placeholder for topic-specific accuracy"""
        return self.knowledge_level


@dataclass
class AffectiveModel:
    """Affective/emotional dimensions of student learning"""
    motivation_level: float = 0.7  # 0-1 scale
    self_efficacy: float = 0.6  # Confidence in abilities
    engagement_level: float = 0.7  # Current engagement
    frustration_level: float = 0.3  # Current frustration
    response_count: int = 0
    
    def update_engagement(self, response_length: int, time_taken: float):
        """
        Update engagement based on interaction patterns.

        response_length: number of characters in response.
        Word count is a more accurate indicator, so we convert chars to words.
        """
        self.response_count += 1

        # Estimate word count from character count (assume avg 5 chars per word + 1 space = ~6 chars/word)
        estimated_word_count = max(1, response_length // 6)

        # Short responses (<3 words) might indicate low engagement
        if estimated_word_count < 3:
            self.engagement_level = max(0.0, self.engagement_level - 0.05)
        else:
            self.engagement_level = min(1.0, self.engagement_level + 0.05)

        # Very long delays might indicate frustration or disengagement
        if time_taken > 30:
            self.frustration_level = min(1.0, self.frustration_level + 0.1)
    
    def update_after_correct(self):
        """Boost confidence and reduce frustration after correct answer"""
        self.self_efficacy = min(1.0, self.self_efficacy + 0.05)
        self.motivation_level = min(1.0, self.motivation_level + 0.03)
        self.frustration_level = max(0.0, self.frustration_level - 0.1)
    
    def update_after_incorrect(self):
        """Adjust after incorrect answer"""
        self.frustration_level = min(1.0, self.frustration_level + 0.08)
        if self.frustration_level > 0.7:
            self.motivation_level = max(0.0, self.motivation_level - 0.05)


@dataclass
class LearningStyleModel:
    """Learning style preferences (Felder-Silverman Model)"""
    active_reflective: float = 0.5  # 0=active, 1=reflective
    sensing_intuitive: float = 0.5  # 0=sensing, 1=intuitive
    visual_verbal: float = 0.5  # 0=visual, 1=verbal
    sequential_global: float = 0.5  # 0=sequential, 1=global
    
    def get_dominant_style(self) -> List[str]:
        """Return dominant learning styles"""
        styles = []
        if self.active_reflective < 0.4:
            styles.append("active")
        elif self.active_reflective > 0.6:
            styles.append("reflective")
        
        if self.sensing_intuitive < 0.4:
            styles.append("sensing")
        elif self.sensing_intuitive > 0.6:
            styles.append("intuitive")
        
        if self.visual_verbal < 0.4:
            styles.append("visual")
        elif self.visual_verbal > 0.6:
            styles.append("verbal")
        
        if self.sequential_global < 0.4:
            styles.append("sequential")
        elif self.sequential_global > 0.6:
            styles.append("global")
        
        return styles if styles else ["balanced"]


@dataclass
class StudentModel:
    """Complete student model combining all dimensions"""
    student_id: str
    cognitive: CognitiveModel = field(default_factory=CognitiveModel)
    affective: AffectiveModel = field(default_factory=AffectiveModel)
    learning_style: LearningStyleModel = field(default_factory=LearningStyleModel)
    session_count: int = 0
    total_study_time: float = 0.0
    last_session: Optional[str] = None
    learning_goals: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "student_id": self.student_id,
            "cognitive": asdict(self.cognitive),
            "affective": asdict(self.affective),
            "learning_style": asdict(self.learning_style),
            "session_count": self.session_count,
            "total_study_time": self.total_study_time,
            "last_session": self.last_session,
            "learning_goals": self.learning_goals
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StudentModel':
        """Create StudentModel from dictionary"""
        cognitive = CognitiveModel(**data["cognitive"])
        affective = AffectiveModel(**data["affective"])
        learning_style = LearningStyleModel(**data["learning_style"])
        
        return cls(
            student_id=data["student_id"],
            cognitive=cognitive,
            affective=affective,
            learning_style=learning_style,
            session_count=data["session_count"],
            total_study_time=data["total_study_time"],
            last_session=data.get("last_session"),
            learning_goals=data.get("learning_goals", [])
        )


@dataclass
class Skill:
    """Represents a skill to be learned"""
    name: str
    description: str
    difficulty: float  # 0-1 scale
    prerequisites: List[str] = field(default_factory=list)
    mastery_level: float = 0.0  # Current mastery 0-1


@dataclass
class LearningGoal:
    """Goal-to-skill mapping"""
    goal_name: str
    description: str
    required_skills: List[Skill] = field(default_factory=list)
    target_date: Optional[str] = None
    progress: float = 0.0
    
    def update_progress(self):
        """Calculate progress based on skill mastery"""
        if not self.required_skills:
            self.progress = 0.0
            return
        
        total_mastery = sum(skill.mastery_level for skill in self.required_skills)
        self.progress = total_mastery / len(self.required_skills)


@dataclass
class LearningPathNode:
    """Node in the adaptive learning path"""
    topic: str
    difficulty: float
    estimated_time: int  # minutes
    questions: List[Dict] = field(default_factory=list)
    completed: bool = False
    attempts: int = 0
    success_rate: float = 0.0


class AdaptiveLearningPath:
    """Manages the learning path with dynamic scheduling"""
    
    def __init__(self, flashcards: List[Dict], student_model: StudentModel):
        self.flashcards = flashcards
        self.student_model = student_model
        self.path: List[LearningPathNode] = []
        self.current_node_index = 0
        self._build_initial_path()
    
    def _build_initial_path(self):
        """Build initial learning path based on flashcards"""
        # Group flashcards by topic/difficulty
        for i, card in enumerate(self.flashcards):
            node = LearningPathNode(
                topic=f"Topic {i+1}",
                difficulty=0.5,  # Default medium difficulty
                estimated_time=5,
                questions=[card]
            )
            self.path.append(node)
    
    def get_next_question(self) -> Optional[Dict]:
        """Get next question based on adaptive algorithm"""
        if self.current_node_index >= len(self.path):
            return None
        
        current_node = self.path[self.current_node_index]
        
        # Adaptive difficulty: adjust based on student performance
        knowledge = self.student_model.cognitive.knowledge_level
        
        # If student is struggling, revisit easier material
        if knowledge < 0.4 and self.current_node_index > 0:
            self.current_node_index = max(0, self.current_node_index - 2)
            current_node = self.path[self.current_node_index]
        
        if current_node.questions:
            return current_node.questions[0]
        
        return None
    
    def update_progress(self, correct: bool):
        """Update path based on student performance"""
        if self.current_node_index < len(self.path):
            node = self.path[self.current_node_index]
            node.attempts += 1
            
            if correct:
                node.success_rate = (node.success_rate * (node.attempts - 1) + 1.0) / node.attempts
                if node.success_rate > 0.7:
                    node.completed = True
                    self.current_node_index += 1
            else:
                node.success_rate = (node.success_rate * (node.attempts - 1)) / node.attempts

