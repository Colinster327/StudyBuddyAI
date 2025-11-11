"""
Database Management for StudyBuddyAI

All SQLite database operations for student profile persistence.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List
from models import StudentModel, CognitiveModel, AffectiveModel, LearningStyleModel


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'


def get_db_path() -> str:
    """Get the path to the SQLite database"""
    return os.path.join(os.path.dirname(__file__), "studybuddy.db")


def init_database():
    """Initialize SQLite database with required tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create student_profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            student_id TEXT PRIMARY KEY,
            session_count INTEGER DEFAULT 0,
            total_study_time REAL DEFAULT 0.0,
            last_session TEXT,
            learning_goals TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create cognitive_model table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cognitive_models (
            student_id TEXT PRIMARY KEY,
            knowledge_level REAL DEFAULT 0.5,
            metacognition_score REAL DEFAULT 0.5,
            attention_span REAL DEFAULT 0.7,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            mastered_topics TEXT,
            struggling_topics TEXT,
            FOREIGN KEY (student_id) REFERENCES student_profiles(student_id)
        )
    """)
    
    # Create affective_model table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS affective_models (
            student_id TEXT PRIMARY KEY,
            motivation_level REAL DEFAULT 0.7,
            self_efficacy REAL DEFAULT 0.6,
            engagement_level REAL DEFAULT 0.7,
            frustration_level REAL DEFAULT 0.3,
            response_count INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES student_profiles(student_id)
        )
    """)
    
    # Create learning_style_model table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_style_models (
            student_id TEXT PRIMARY KEY,
            active_reflective REAL DEFAULT 0.5,
            sensing_intuitive REAL DEFAULT 0.5,
            visual_verbal REAL DEFAULT 0.5,
            sequential_global REAL DEFAULT 0.5,
            FOREIGN KEY (student_id) REFERENCES student_profiles(student_id)
        )
    """)
    
    # Create session_history table for tracking individual sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            session_date TEXT,
            duration_minutes REAL,
            questions_answered INTEGER,
            correct_answers INTEGER,
            knowledge_level REAL,
            engagement_level REAL,
            FOREIGN KEY (student_id) REFERENCES student_profiles(student_id)
        )
    """)
    
    conn.commit()
    conn.close()


def load_student_profile(student_id: str = "default") -> StudentModel:
    """Load student profile from SQLite database or create new one"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if profile exists
    cursor.execute("SELECT * FROM student_profiles WHERE student_id = ?", (student_id,))
    profile_row = cursor.fetchone()
    
    if profile_row:
        # Load existing profile
        print(f"{Colors.GREEN}✓ Loaded existing profile for {student_id}{Colors.END}")
        
        # Get profile data
        _, session_count, total_study_time, last_session, learning_goals_json, _, _ = profile_row
        learning_goals = json.loads(learning_goals_json) if learning_goals_json else []
        
        # Get cognitive model
        cursor.execute("SELECT * FROM cognitive_models WHERE student_id = ?", (student_id,))
        cog_row = cursor.fetchone()
        cognitive = CognitiveModel(
            knowledge_level=cog_row[1],
            metacognition_score=cog_row[2],
            attention_span=cog_row[3],
            correct_answers=cog_row[4],
            total_answers=cog_row[5],
            mastered_topics=json.loads(cog_row[6]) if cog_row[6] else [],
            struggling_topics=json.loads(cog_row[7]) if cog_row[7] else []
        )
        
        # Get affective model
        cursor.execute("SELECT * FROM affective_models WHERE student_id = ?", (student_id,))
        aff_row = cursor.fetchone()
        affective = AffectiveModel(
            motivation_level=aff_row[1],
            self_efficacy=aff_row[2],
            engagement_level=aff_row[3],
            frustration_level=aff_row[4],
            response_count=aff_row[5]
        )
        
        # Get learning style model
        cursor.execute("SELECT * FROM learning_style_models WHERE student_id = ?", (student_id,))
        style_row = cursor.fetchone()
        learning_style = LearningStyleModel(
            active_reflective=style_row[1],
            sensing_intuitive=style_row[2],
            visual_verbal=style_row[3],
            sequential_global=style_row[4]
        )
        
        conn.close()
        
        return StudentModel(
            student_id=student_id,
            cognitive=cognitive,
            affective=affective,
            learning_style=learning_style,
            session_count=session_count,
            total_study_time=total_study_time,
            last_session=last_session,
            learning_goals=learning_goals
        )
    else:
        # Create new profile
        print(f"{Colors.CYAN}Creating new profile for {student_id}{Colors.END}")
        conn.close()
        return StudentModel(student_id=student_id)


def save_student_profile(model: StudentModel):
    """Save student profile to SQLite database"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Save or update student profile
        cursor.execute("""
            INSERT OR REPLACE INTO student_profiles 
            (student_id, session_count, total_study_time, last_session, learning_goals, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            model.student_id,
            model.session_count,
            model.total_study_time,
            model.last_session,
            json.dumps(model.learning_goals),
            datetime.now().isoformat()
        ))
        
        # Save cognitive model
        cursor.execute("""
            INSERT OR REPLACE INTO cognitive_models 
            (student_id, knowledge_level, metacognition_score, attention_span, 
             correct_answers, total_answers, mastered_topics, struggling_topics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model.student_id,
            model.cognitive.knowledge_level,
            model.cognitive.metacognition_score,
            model.cognitive.attention_span,
            model.cognitive.correct_answers,
            model.cognitive.total_answers,
            json.dumps(model.cognitive.mastered_topics),
            json.dumps(model.cognitive.struggling_topics)
        ))
        
        # Save affective model
        cursor.execute("""
            INSERT OR REPLACE INTO affective_models 
            (student_id, motivation_level, self_efficacy, engagement_level, 
             frustration_level, response_count)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            model.student_id,
            model.affective.motivation_level,
            model.affective.self_efficacy,
            model.affective.engagement_level,
            model.affective.frustration_level,
            model.affective.response_count
        ))
        
        # Save learning style model
        cursor.execute("""
            INSERT OR REPLACE INTO learning_style_models 
            (student_id, active_reflective, sensing_intuitive, 
             visual_verbal, sequential_global)
            VALUES (?, ?, ?, ?, ?)
        """, (
            model.student_id,
            model.learning_style.active_reflective,
            model.learning_style.sensing_intuitive,
            model.learning_style.visual_verbal,
            model.learning_style.sequential_global
        ))
        
        conn.commit()
        print(f"{Colors.GREEN}✓ Profile saved to database{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}Error saving profile: {e}{Colors.END}")
        conn.rollback()
    finally:
        conn.close()


def save_session_history(model: StudentModel, duration: float, questions: int, correct: int):
    """Save session history for analytics"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO session_history 
            (student_id, session_date, duration_minutes, questions_answered, 
             correct_answers, knowledge_level, engagement_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            model.student_id,
            datetime.now().isoformat(),
            duration,
            questions,
            correct,
            model.cognitive.knowledge_level,
            model.affective.engagement_level
        ))
        conn.commit()
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not save session history: {e}{Colors.END}")
    finally:
        conn.close()


def get_session_history(student_id: str, limit: int = 10) -> List[Dict]:
    """Get recent session history for a student"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT session_date, duration_minutes, questions_answered, 
               correct_answers, knowledge_level, engagement_level
        FROM session_history
        WHERE student_id = ?
        ORDER BY session_date DESC
        LIMIT ?
    """, (student_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "date": row[0],
            "duration": row[1],
            "questions": row[2],
            "correct": row[3],
            "knowledge": row[4],
            "engagement": row[5]
        })
    
    return history

