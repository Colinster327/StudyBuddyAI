# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        StudyBuddyAI                             │
│              Research-Backed Personalized Tutor                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Student Interaction Layer                    │
├─────────────────────────────────────────────────────────────────┤
│  • Voice Input (RealtimeSTT)                                    │
│  • Real-time Metrics Display                                    │
│  • Conversational AI Response (GPT-5)                           │
│  • Session Management                                           │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Student Modeling System                       │
│                         (Paper 1)                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Cognitive   │  │  Affective   │  │   Learning   │          │
│  │    Model     │  │    Model     │  │    Style     │          │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤          │
│  │• Knowledge   │  │• Motivation  │  │• Active vs   │          │
│  │• Mastery     │  │• Engagement  │  │  Reflective  │          │
│  │• Accuracy    │  │• Frustration │  │• Visual vs   │          │
│  │• Topics      │  │• Efficacy    │  │  Verbal      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Adaptive Teaching System                       │
│                      (Paper 1 & 2)                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         Adaptive Prompt Generation (Paper 1)              │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Knowledge-based adaptation                             │  │
│  │  • Affective state adaptation                             │  │
│  │  • Learning style matching                                │  │
│  │  • Dynamic difficulty adjustment                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                               │                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │      Adaptive Learning Path (Paper 2)                     │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │  • Goal-to-skill mapping                                  │  │
│  │  • Dynamic path scheduling                                │  │
│  │  • Remediation logic                                      │  │
│  │  • Success rate tracking                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Feedback & Analysis Layer                     │
│                         (Paper 1)                                │
├─────────────────────────────────────────────────────────────────┤
│  • Real-time performance analysis                               │
│  • Learning style inference                                     │
│  • Engagement monitoring                                        │
│  • AI-generated session summaries                               │
│  • Teaching strategy recommendations                            │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Persistence Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  • JSON profile storage                                         │
│  • Cross-session continuity                                     │
│  • Historical tracking                                          │
│  • Progress statistics                                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
Session Start
     │
     ▼
┌─────────────────────┐
│ Load/Create Profile │
│  (profile_*.json)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Initialize Models  │
│ • StudentModel      │
│ • LearningPath      │
│ • Skills/Goals      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Adaptive  │
│   System Prompt     │
└──────────┬──────────┘
           │
           ▼
     ┌─────────┐
     │ Display │
     │ Profile │
     └────┬────┘
          │
          ▼
    ╔═══════════╗
    ║   Study   ║  <──────┐
    ║   Loop    ║         │
    ╚═════╤═════╝         │
          │               │
          ▼               │
    ┌──────────┐          │
    │  Record  │          │
    │   Voice  │          │
    └────┬─────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │  Update  │          │
    │Engagement│          │
    └────┬─────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │   Send   │          │
    │  to LLM  │          │
    └────┬─────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │ Analyze  │          │
    │ Response │          │
    └────┬─────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │  Update  │          │
    │  Models  │          │
    └────┬─────┘          │
         │                │
         ▼                │
    ┌──────────┐          │
    │ Display  │          │
    │ Metrics  │          │
    └────┬─────┘          │
         │                │
         └────────────────┘
          
     [Ctrl+C]
          │
          ▼
    ┌──────────┐
    │ Generate │
    │ Summary  │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │ Display  │
    │  Stats   │
    └────┬─────┘
         │
         ▼
    ┌──────────┐
    │   Save   │
    │ Profile  │
    └────┬─────┘
         │
         ▼
    Session End
```

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Input                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   record_text()      │
              │  - Capture voice     │
              │  - Measure time      │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   ask_openai()       │
              │  - Update engagement │
              │  - Infer style       │
              └──────────┬───────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
    ┌───────────┐ ┌───────────┐ ┌───────────┐
    │Cognitive  │ │Affective  │ │Learning   │
    │Model      │ │Model      │ │Style      │
    │update     │ │update     │ │inference  │
    └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ analyze_student_     │
              │    response()        │
              │ - Detect correctness │
              │ - Update knowledge   │
              │ - Update path        │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ display_learning_    │
              │    metrics()         │
              │ - Show knowledge     │
              │ - Show engagement    │
              └──────────────────────┘
```

## Student Model Structure

```
StudentModel
├── student_id: str
├── session_count: int
├── total_study_time: float
├── last_session: datetime
├── learning_goals: List[str]
│
├── CognitiveModel
│   ├── knowledge_level: float (0-1)
│   ├── metacognition_score: float (0-1)
│   ├── attention_span: float (0-1)
│   ├── correct_answers: int
│   ├── total_answers: int
│   ├── mastered_topics: List[str]
│   └── struggling_topics: List[str]
│
├── AffectiveModel
│   ├── motivation_level: float (0-1)
│   ├── self_efficacy: float (0-1)
│   ├── engagement_level: float (0-1)
│   ├── frustration_level: float (0-1)
│   └── response_count: int
│
└── LearningStyleModel (Felder-Silverman)
    ├── active_reflective: float (0-1)
    ├── sensing_intuitive: float (0-1)
    ├── visual_verbal: float (0-1)
    └── sequential_global: float (0-1)
```

## Adaptive Learning Path Structure

```
AdaptiveLearningPath
├── flashcards: List[Dict]
├── student_model: StudentModel
├── current_node_index: int
│
└── path: List[LearningPathNode]
    │
    └── LearningPathNode
        ├── topic: str
        ├── difficulty: float (0-1)
        ├── estimated_time: int (minutes)
        ├── questions: List[Dict]
        ├── completed: bool
        ├── attempts: int
        └── success_rate: float (0-1)
```

## Goal-Skill Mapping Structure

```
LearningGoal
├── goal_name: str
├── description: str
├── target_date: Optional[str]
├── progress: float (0-1)
│
└── required_skills: List[Skill]
    │
    └── Skill
        ├── name: str
        ├── description: str
        ├── difficulty: float (0-1)
        ├── prerequisites: List[str]
        └── mastery_level: float (0-1)
```

## Adaptation Decision Tree

```
                    ┌──────────────┐
                    │ User Response│
                    └──────┬───────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Analyze Response│
                  │ - Length        │
                  │ - Time taken    │
                  │ - Content       │
                  └────────┬────────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   Cognitive  │ │  Affective   │ │ Learning     │
    │   Updates    │ │   Updates    │ │ Style Update │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           │   ┌────────────┴────────────┐   │
           │   │                         │   │
           ▼   ▼                         ▼   ▼
    ┌────────────────┐            ┌────────────────┐
    │ Knowledge < 40%│            │Learning Style  │
    │      ?         │            │  Detection     │
    └────────┬───────┘            └────────────────┘
             │                           │
          Yes│  No                       │
             │  │                        │
    ┌────────▼──▼────────┐               │
    │  Adjust Difficulty │               │
    │  - Easy: Go back   │               │
    │  - Hard: Continue  │               │
    └────────┬───────────┘               │
             │                            │
             └────────────┬───────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │ Regenerate Prompt│
                │  - Knowledge     │
                │  - Affective     │
                │  - Style         │
                └──────────────────┘
```

## Session Lifecycle

```
┌──────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                         │
└──────────────────────────────────────────────────────────────┘

1. INITIALIZATION
   ┌──────────────┐
   │ Load Profile │  → Existing: Restore state
   └──────┬───────┘  → New: Create with defaults
          │
          ▼
   ┌──────────────┐
   │ Build Path   │  → Create learning path from flashcards
   └──────┬───────┘  → Initialize with student's level
          │
          ▼
   ┌──────────────┐
   │ Map Goals    │  → Identify required skills
   └──────┬───────┘  → Set mastery targets
          │
          ▼
   ┌──────────────┐
   │Generate      │  → Create personalized system prompt
   │Prompt        │  → Embed student model data
   └──────┬───────┘
          │
          ▼

2. ACTIVE LEARNING
   ╔══════════════╗
   ║  Study Loop  ║  (Repeats)
   ╚══════╤═══════╝
          │
          ▼
   ┌──────────────┐
   │ Voice Input  │  → Record student question
   └──────┬───────┘  → Measure engagement signals
          │
          ▼
   ┌──────────────┐
   │ AI Response  │  → Generate adaptive answer
   └──────┬───────┘  → Match to learning style
          │
          ▼
   ┌──────────────┐
   │ Update Model │  → Cognitive: knowledge, mastery
   └──────┬───────┘  → Affective: motivation, engagement
          │          → Style: infer preferences
          ▼
   ┌──────────────┐
   │Show Metrics  │  → Display knowledge %
   └──────┬───────┘  → Display engagement %
          │
          └──────────────┐
                         │
                (Back to Study Loop)

3. SESSION END
   ┌──────────────┐
   │Generate      │  → AI analyzes session
   │Summary       │  → Provides recommendations
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │Display Stats │  → Show duration, accuracy
   └──────┬───────┘  → Show progress metrics
          │
          ▼
   ┌──────────────┐
   │Save Profile  │  → Persist to JSON
   └──────┬───────┘  → Update session count
          │
          ▼
   ┌──────────────┐
   │   Goodbye    │
   └──────────────┘
```

## Key Algorithms

### 1. Knowledge Level Update (Moving Average)
```
new_knowledge = 0.7 × old_knowledge + 0.3 × current_accuracy

Where:
  current_accuracy = correct_answers / total_answers
```

### 2. Engagement Update
```
if response_length < 10:
    engagement -= 0.05
else:
    engagement += 0.05

if response_time > 30 seconds:
    frustration += 0.10

engagement = clamp(engagement, 0.0, 1.0)
```

### 3. Learning Path Remediation
```
if knowledge_level < 0.4 AND current_index > 0:
    current_index = max(0, current_index - 2)  # Go back

if node.success_rate > 0.7:
    node.completed = True
    current_index += 1  # Advance
```

### 4. Learning Style Inference
```
For each keyword category:
    if keyword_found:
        dimension += direction × 0.05
        dimension = clamp(dimension, 0.0, 1.0)

Examples:
  "example" → sensing_intuitive -= 0.05  (more sensing)
  "theory"  → sensing_intuitive += 0.05  (more intuitive)
  "visual"  → visual_verbal -= 0.05      (more visual)
```

### 5. Success Rate Calculation
```
new_rate = (old_rate × (attempts - 1) + result) / attempts

Where:
  result = 1.0 if correct else 0.0
```

## File Dependencies

```
main.py (349 lines)
├── imports
│   ├── RealtimeSTT (voice recording)
│   ├── OpenAI (LLM interaction)
│   ├── models.py (data structures)
│   ├── database.py (persistence)
│   ├── adaptive_learning.py (adaptive teaching)
│   └── student_analysis.py (analysis & metrics)
│
├── reads
│   └── os-flashcards.json (study material)
│
└── orchestrates all modules

models.py (265 lines)
└── Pure data structures (no dependencies)

database.py (313 lines)
├── imports models.py
└── manages studybuddy.db (SQLite)

adaptive_learning.py (184 lines)
├── imports models.py
└── generates adaptive prompts & manages skills

student_analysis.py (79 lines)
├── imports models.py
└── analyzes responses & displays metrics
```

## External Integrations

```
┌─────────────────┐
│  StudyBuddyAI   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│OpenAI  │ │Realtime│
│ API    │ │  STT   │
└────────┘ └────────┘
│ GPT-5    │ Whisper
│ Chat     │ Audio
└──────────┴─────────┘
```

## Conclusion

This architecture implements a complete Intelligent Tutoring System that:

1. **Models** students across multiple dimensions
2. **Adapts** teaching in real-time based on student state
3. **Tracks** progress across sessions
4. **Optimizes** learning paths dynamically
5. **Persists** insights for continuous improvement

The design is modular, extensible, and grounded in published research, making it both theoretically sound and practically effective.

