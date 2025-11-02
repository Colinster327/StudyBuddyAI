# StudyBuddyAI Requirements

## Checkpoint 1. A complete demo with manual prompts (GenAI App Rapid Prototyping)

### App Overview
StudyBuddyAI is a voice-based, AI-powered study assistant that helps students prepare for their Operating Systems exam. The app loads flashcard material into the AI's context and acts as an interactive study buddy.

### Manual Prompts Demo (Intended Inputs and Outputs)

#### Example Input 1: Quiz Request
**User Input:** "Can you quiz me on some Operating Systems concepts?"

**Expected Output:** 
The AI should select a question from the loaded flashcards and ask it in a friendly, conversational manner. For example:
"Sure! Let's test your knowledge. Here's a question: What is dual mode operation in an operating system?"

#### Example Input 2: Concept Explanation
**User Input:** "What is the difference between fork and exec?"

**Expected Output:**
The AI should explain the concept clearly, referencing the flashcard material:
"Great question! fork() creates a new process by duplicating the calling process - the child gets a copy of the parent's address space. After a fork(), exec() replaces the current process image with a new program, keeping the same PID and file descriptors. So fork creates a copy, exec replaces it with something new."

#### Example Input 3: Study Session Start
**User Input:** "I want to study for my OS exam"

**Expected Output:**
The AI should respond encouragingly and offer study options:
"I'd be happy to help you study for your Operating Systems exam! I have 20 flashcards covering topics like dual mode operation, interrupts, system calls, fork/exec, file descriptors, pipes, and more. Would you like me to quiz you, or would you prefer to ask questions about specific topics?"

#### Example Input 4: Clarification Request
**User Input:** "I'm confused about file descriptors"

**Expected Output:**
The AI should provide a clear, supportive explanation with examples:
"No problem, let me explain! File descriptors are integer handles that represent open files or I/O resources. By convention, 0 is stdin (standard input), 1 is stdout (standard output), and 2 is stderr (standard error). When you open a file in your program, the operating system gives you a file descriptor number that you use to read from or write to that file. Think of it like a ticket number at the DMV - it's just a way to keep track of which file you're working with!"

### Acceptance Criteria for Outputs

1. **Accuracy**: All responses must be factually correct and consistent with the flashcard material provided
2. **Tone**: Responses should be friendly, encouraging, and patient - matching a supportive study buddy persona
3. **Relevance**: Answers should directly address the student's question or request
4. **Clarity**: Explanations should be clear and understandable, avoiding overly technical jargon when possible
5. **Interactivity**: The AI should proactively offer quiz questions when requested and engage in back-and-forth dialogue
6. **Context Awareness**: The AI should reference the 20 flashcards in its context and use them as the primary knowledge base
7. **Encouragement**: The AI should provide positive reinforcement and support the student's learning process

### Feasibility Assessment

The GenAI app proposal is feasible because:
- The flashcard content is loaded into the system prompt at initialization
- The AI model (GPT-5) has sufficient capability to act as a study buddy
- Voice input/output is handled by RealtimeSTT and OpenAI's API
- The conversational nature allows for flexible interaction patterns
- The scope is well-defined (Operating Systems exam preparation)

