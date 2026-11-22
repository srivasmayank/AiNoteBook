"""
=============================================================================
DAY 3: CONVERSATIONAL STATE & THE STEP-BY-STEP LEARNING LOOP
=============================================================================
Concepts taught in this file:
1. Stateful vs. Stateless systems in Generative AI.
2. Context Window & Multi-turn conversation history.
3. Tracking learner state (current module, current lesson, progress).
4. Building the interactive 'next' command teaching loop.
5. Capturing doubts in-flight without losing teaching continuity.
=============================================================================
"""

import os
import json
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# =============================================================================
# 1. LEARNER STATE MODEL
# =============================================================================
# Large Language Models are completely STATELESS by nature.
# They do NOT remember past questions unless we pass that history back to them!
# Here we define the explicit state structure our system maintains.

class DoubtRecord(BaseModel):
    module_title: str
    lesson_title: str
    question: str
    answer: str


class LearningSessionState(BaseModel):
    subject: str
    current_module_idx: int = 0
    current_lesson_idx: int = 0
    completed_lessons: List[str] = Field(default_factory=list)
    recorded_doubts: List[DoubtRecord] = Field(default_factory=list)
    lesson_chat_history: List[Dict[str, str]] = Field(default_factory=list)


# =============================================================================
# 2. SYSTEM PROMPT FOR STEP-BY-STEP TEACHING
# =============================================================================
TEACHER_SYSTEM_PROMPT = """
You are the interactive Step-by-Step AI Tutor for 'AI Notebook'.
You teach one lesson at a time. Never rush into future lessons.

When teaching a lesson, follow this structure:
1. 🎯 Lesson Title & Big Idea (One clear sentence on what this is)
2. 💡 Intuition (A simple real-world analogy)
3. ❓ Why Does It Exist? (What problem does it solve in engineering?)
4. 💻 Practical Code Example (Clean code with line-by-line explanation)
5. ⚠️ Common Beginner Trap (What mistake beginners make)
6. ❓ Concept Check (One quick question to test understanding)

End with: "Type your doubt, or type 'next' to proceed to the next lesson."
"""


# =============================================================================
# 3. LLM CALL HELPERS
# =============================================================================
def call_llm(messages: List[Dict[str, str]], temperature: float = 0.5) -> str:
    """Calls Gemini or OpenAI with multi-turn messages array."""
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)

        # Convert standard message format to Gemini contents
        contents = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

        config = types.GenerateContentConfig(
            system_instruction=TEACHER_SYSTEM_PROMPT,
            temperature=temperature,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
        )
        return response.text

    elif OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        formatted_messages = [{"role": "system", "content": TEACHER_SYSTEM_PROMPT}] + messages
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=formatted_messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    else:
        # Fallback simulator for offline mode
        last_msg = messages[-1]["content"] if messages else ""
        if "Explain Lesson:" in last_msg:
            return (
                "🎯 Big Idea: Understanding this lesson concept.\n"
                "💡 Intuition: Think of it like a train station timetable.\n"
                "❓ Why It Exists: Without it, your application would lock up and freeze.\n"
                "💻 Practical Code Example:\n"
                "   # Basic example\n"
                "   print('Step 1 executed')\n"
                "⚠️ Common Trap: Forgetting to handle errors.\n"
                "❓ Concept Check: Can you tell me what happens if an error is thrown?\n\n"
                "Type your doubt, or type 'next' to proceed to the next lesson."
            )
        else:
            return (
                f"🤖 [Simulated Tutor Answer to: '{last_msg}']\n"
                "Great question! When that happens, the system executes the fallback handler first, "
                "ensuring that resources are released cleanly before moving to the next cycle.\n\n"
                "Type another question, or type 'next' to continue."
            )


# =============================================================================
# 4. STEP-BY-STEP TUTOR ENGINE
# =============================================================================
class StepByStepTutor:
    def __init__(self, curriculum_path: str):
        self.curriculum = self._load_curriculum(curriculum_path)
        self.state = LearningSessionState(subject=self.curriculum.get("subject", "General Tech"))

    def _load_curriculum(self, path: str) -> dict:
        """Loads curriculum from Day 2 JSON file, or creates default."""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        # Default fallback curriculum if file is not found
        return {
            "subject": "Python Basics",
            "modules": [
                {
                    "module_number": 1,
                    "title": "Python Foundations",
                    "lessons": [
                        {"title": "Variables & Memory", "description": "How Python stores values."},
                        {"title": "Data Types & Collections", "description": "Lists, Dictionaries, and Tuples."}
                    ]
                },
                {
                    "module_number": 2,
                    "title": "Logic & Functions",
                    "lessons": [
                        {"title": "Conditionals & Loops", "description": "Controlling code flow."},
                        {"title": "Functions & Reusability", "description": "Writing modular code."}
                    ]
                }
            ]
        }

    def get_current_lesson(self) -> Optional[dict]:
        """Returns the current lesson based on state indices."""
        modules = self.curriculum.get("modules", [])
        if self.state.current_module_idx < len(modules):
            current_mod = modules[self.state.current_module_idx]
            lessons = current_mod.get("lessons", [])
            if self.state.current_lesson_idx < len(lessons):
                return {
                    "module_title": current_mod.get("title"),
                    "module_num": current_mod.get("module_number", self.state.current_module_idx + 1),
                    "lesson": lessons[self.state.current_lesson_idx],
                    "total_modules": len(modules),
                    "total_lessons_in_mod": len(lessons),
                }
        return None

    def teach_lesson(self) -> str:
        """Instructs the AI to deliver the current lesson."""
        info = self.get_current_lesson()
        if not info:
            return "🎉 Congratulations! You have completed all modules and lessons in this course!"

        lesson = info["lesson"]
        prompt = (
            f"Please teach the following lesson now:\n"
            f"Subject: {self.state.subject}\n"
            f"Module: {info['module_title']}\n"
            f"Lesson Title: {lesson['title']}\n"
            f"Lesson Goal: {lesson.get('description', '')}\n"
            f"Key Concepts: {', '.join(lesson.get('key_concepts', []))}"
        )

        # Reset lesson chat history for the new lesson
        self.state.lesson_chat_history = [{"role": "user", "content": prompt}]

        # Call AI
        explanation = call_llm(self.state.lesson_chat_history, temperature=0.4)
        self.state.lesson_chat_history.append({"role": "model", "content": explanation})
        return explanation

    def answer_doubt(self, user_question: str) -> str:
        """Answers a user doubt using the multi-turn context of the current lesson."""
        info = self.get_current_lesson()
        module_title = info["module_title"] if info else "General"
        lesson_title = info["lesson"]["title"] if info else "General"

        # Append student's doubt to multi-turn conversation
        self.state.lesson_chat_history.append({"role": "user", "content": user_question})

        answer = call_llm(self.state.lesson_chat_history, temperature=0.6)
        self.state.lesson_chat_history.append({"role": "model", "content": answer})

        # Save doubt for future Living Notes and Revision!
        self.state.recorded_doubts.append(
            DoubtRecord(
                module_title=module_title,
                lesson_title=lesson_title,
                question=user_question,
                answer=answer,
            )
        )
        return answer

    def advance_next(self) -> str:
        """Advances to the next lesson or next module when user types 'next'."""
        info = self.get_current_lesson()
        if not info:
            return "Course already finished!"

        # Mark lesson as completed
        completed_title = f"{info['module_title']} → {info['lesson']['title']}"
        if completed_title not in self.state.completed_lessons:
            self.state.completed_lessons.append(completed_title)

        # Advance lesson index
        self.state.current_lesson_idx += 1

        # Check if we reached the end of current module
        modules = self.curriculum.get("modules", [])
        current_mod = modules[self.state.current_module_idx]
        if self.state.current_lesson_idx >= len(current_mod.get("lessons", [])):
            self.state.current_module_idx += 1
            self.state.current_lesson_idx = 0

        # Check if course is complete
        if self.state.current_module_idx >= len(modules):
            return "🎓 You have completed all lessons in this curriculum! Type 'status' to review your progress."

        # Teach the new lesson
        return self.teach_lesson()

    def get_status(self) -> str:
        """Returns human-readable learning progress."""
        modules = self.curriculum.get("modules", [])
        total_lessons = sum(len(m.get("lessons", [])) for m in modules)
        completed_count = len(self.state.completed_lessons)
        percent = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0

        status_text = (
            f"\n📊 LEARNING PROGRESS DASHBOARD:\n"
            f"   • Subject: {self.state.subject}\n"
            f"   • Progress: {percent}% ({completed_count}/{total_lessons} lessons completed)\n"
            f"   • Doubts Asked & Saved: {len(self.state.recorded_doubts)}\n"
            f"   • Completed Lessons:\n"
        )
        for cl in self.state.completed_lessons:
            status_text += f"      ✅ {cl}\n"
        return status_text


# =============================================================================
# 5. CLI INTERACTIVE EXECUTION
# =============================================================================
def main():
    curriculum_file = os.path.join(os.path.dirname(__file__), "sample_curriculum.json")
    tutor = StepByStepTutor(curriculum_file)

    print("=" * 70)
    print(" 🧑‍🏫 AI NOTEBOOK — DAY 3: STEP-BY-STEP INTERACTIVE TUTOR")
    print("=" * 70)
    print(f"Loaded Course: '{tutor.state.subject}'")
    print("Commands:")
    print("  • Type 'next'   -> Proceed to the next lesson")
    print("  • Type 'status' -> View current learning progress and saved doubts")
    print("  • Type 'exit'   -> Quit session")
    print("  • Or type ANY question/doubt to discuss the current lesson!\n")
    print("=" * 70)

    # Begin teaching the first lesson
    first_lesson = tutor.teach_lesson()
    print(f"\n🤖 AI Tutor:\n{first_lesson}\n")
    print("-" * 70)

    while True:
        try:
            user_input = input("🧑 You: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! Great progress on Day 3.")
                break

            elif user_input.lower() == "next":
                print("\n⏩ Moving to the next lesson...\n")
                reply = tutor.advance_next()
                print(f"🤖 AI Tutor:\n{reply}\n")
                print("-" * 70)

            elif user_input.lower() == "status":
                print(tutor.get_status())
                print("-" * 70)

            else:
                # User asked a doubt or question
                print("\n🤖 AI Tutor clarifying your doubt in context...\n")
                answer = tutor.answer_doubt(user_input)
                print(f"🤖 AI Tutor:\n{answer}\n")
                print(f"📌 [Note: This doubt has been saved to '{tutor.get_current_lesson()['lesson']['title']}']")
                print("-" * 70)

        except KeyboardInterrupt:
            print("\nSession paused.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
