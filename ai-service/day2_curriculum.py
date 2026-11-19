"""
=============================================================================
DAY 2: DETERMINISTIC STRUCTURED OUTPUT & THE CURRICULUM GENERATOR
=============================================================================
Concepts taught in this file:
1. Why LLMs naturally output unpredictable conversational text.
2. How to force an LLM to return strictly valid JSON.
3. Using Pydantic schemas for data validation in Python.
4. Setting Temperature low (0.1 - 0.2) for structural precision.
5. Building the Curriculum Generator for 'AI Notebook'.
=============================================================================
"""

import os
import json
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# 1. Load API keys from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# =============================================================================
# 2. DEFINE THE DATA SCHEMAS USING PYDANTIC
# =============================================================================
# Pydantic models serve two purposes:
# 1. They tell the LLM EXACTLY what shape of JSON to generate.
# 2. They validate that the Python dictionary actually contains all required fields.

class LessonSchema(BaseModel):
    title: str = Field(description="Clear title of the lesson")
    description: str = Field(description="Summary of what the student will learn in this lesson")
    key_concepts: List[str] = Field(description="3-4 bullet points of core concepts covered")
    estimated_minutes: int = Field(description="Estimated time to complete in minutes")


class ModuleSchema(BaseModel):
    module_number: int = Field(description="Sequential module number starting from 1")
    title: str = Field(description="Title of the module (e.g., 'React Hooks')")
    description: str = Field(description="High-level goal of this module")
    lessons: List[LessonSchema] = Field(description="List of lessons in this module")


class CurriculumSchema(BaseModel):
    subject: str = Field(description="The subject requested by the student")
    level: str = Field(description="Target difficulty level, e.g., 'Beginner to Advanced'")
    prerequisites: List[str] = Field(description="Concepts or tools the student should know beforehand")
    learning_objectives: List[str] = Field(description="Key skills the student will master by the end")
    modules: List[ModuleSchema] = Field(description="The complete sequence of learning modules")


# =============================================================================
# 3. DEFINE SYSTEM PROMPT FOR CURRICULUM DESIGN
# =============================================================================
CURRICULUM_SYSTEM_PROMPT = """
You are an expert curriculum designer and senior technical instructor.
Your task is to design a comprehensive, progressive learning syllabus for any requested technical subject.

Rules:
1. Divide the subject into 4 to 6 logical modules ranging from foundational to advanced.
2. Each module must contain 2 to 4 progressive lessons.
3. Do not skip critical foundational prerequisites.
4. Output MUST conform strictly to the requested JSON schema.
"""


def generate_curriculum_gemini(subject: str) -> dict:
    """Forces Google Gemini to generate JSON matching our CurriculumSchema."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"Design a complete, step-by-step learning curriculum for: '{subject}'"

    # Notice: response_mime_type="application/json" and response_schema=CurriculumSchema
    # This guarantees the model returns 100% valid JSON matching our class!
    config = types.GenerateContentConfig(
        system_instruction=CURRICULUM_SYSTEM_PROMPT,
        temperature=0.2,  # Low temperature for structured data
        response_mime_type="application/json",
        response_schema=CurriculumSchema,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config,
    )

    # Parse the JSON string into a native Python dictionary
    return json.loads(response.text)


def generate_curriculum_openai(subject: str) -> dict:
    """Forces OpenAI GPT-4o-mini to return structured JSON using Pydantic."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"Design a complete, step-by-step learning curriculum for: '{subject}'"

    # OpenAI structured outputs parsing
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": CURRICULUM_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format=CurriculumSchema,
        temperature=0.2,
    )

    return completion.choices[0].message.parsed.model_dump()


def get_curriculum(subject: str) -> dict:
    """Routes the request to the active AI provider or returns a simulated curriculum."""
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        return generate_curriculum_gemini(subject)
    elif OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        return generate_curriculum_openai(subject)
    else:
        # Fallback simulator if no API key is configured yet
        print("\n⚠️ No API key detected. Generating simulated structured curriculum...\n")
        return {
            "subject": subject,
            "level": "Beginner to Advanced",
            "prerequisites": ["Basic computer literacy", "Curiosity to learn"],
            "learning_objectives": [
                f"Master core concepts of {subject}",
                "Write clean, production-ready code",
                "Debug common real-world errors"
            ],
            "modules": [
                {
                    "module_number": 1,
                    "title": f"{subject} Fundamentals",
                    "description": "Understanding core syntax, setup, and mental models.",
                    "lessons": [
                        {
                            "title": "Introduction & Setup",
                            "description": "Installing dependencies and writing your first script.",
                            "key_concepts": ["Installation", "Environment", "First Program"],
                            "estimated_minutes": 20
                        },
                        {
                            "title": "Core Syntax & Types",
                            "description": "Variables, data structures, and operators.",
                            "key_concepts": ["Data Types", "Variables", "Operators"],
                            "estimated_minutes": 30
                        }
                    ]
                },
                {
                    "module_number": 2,
                    "title": "Control Flow & Logic",
                    "description": "Making decisions and looping through data.",
                    "lessons": [
                        {
                            "title": "Conditionals & Branches",
                            "description": "Using if/else logic to control execution.",
                            "key_concepts": ["if statements", "Booleans", "Comparison"],
                            "estimated_minutes": 25
                        },
                        {
                            "title": "Loops & Iteration",
                            "description": "Repeating tasks efficiently.",
                            "key_concepts": ["for loops", "while loops", "break/continue"],
                            "estimated_minutes": 35
                        }
                    ]
                }
            ]
        }


# =============================================================================
# 4. INTERACTIVE CLI RUNNER
# =============================================================================
def main():
    print("=" * 70)
    print(" 📚 AI NOTEBOOK — DAY 2: STRUCTURED CURRICULUM GENERATOR")
    print("=" * 70)
    print("What topic would you like to generate a course curriculum for?")
    print("Examples: 'React Mastery', 'Python for Beginners', 'Docker & Kubernetes'\n")

    subject = input("🎯 Enter Subject (or press Enter for 'React Hooks'): ").strip()
    if not subject:
        subject = "React Hooks"

    print(f"\n🧠 AI is analyzing prerequisites and generating structured curriculum for '{subject}'...")
    curriculum = get_curriculum(subject)

    # Print formatted human-readable summary
    print("\n" + "=" * 70)
    print(f"📖 CURRICULUM: {curriculum['subject'].upper()} ({curriculum['level']})")
    print("=" * 70)
    print(f"🔹 Prerequisites: {', '.join(curriculum['prerequisites'])}")
    print(f"🔹 Learning Objectives:")
    for obj in curriculum['learning_objectives']:
        print(f"   • {obj}")

    print("\n📦 MODULES & LESSONS:")
    for mod in curriculum['modules']:
        print(f"\n  Module {mod['module_number']}: {mod['title']}")
        print(f"  Description: {mod['description']}")
        for les in mod['lessons']:
            print(f"     └─ 📝 {les['title']} ({les['estimated_minutes']} min)")
            print(f"        Concepts: {', '.join(les['key_concepts'])}")

    # Save to a JSON file so our future Express backend can read it!
    output_filename = os.path.join(os.path.dirname(__file__), "sample_curriculum.json")
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(curriculum, f, indent=2)

    print("\n" + "=" * 70)
    print(f"💾 Structured JSON successfully saved to: {output_filename}")
    print("=" * 70)


if __name__ == "__main__":
    main()
