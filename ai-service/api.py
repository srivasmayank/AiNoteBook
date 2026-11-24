"""
=============================================================================
DAY 4: THE PYTHON AI MICROSERVICE (FASTAPI)
=============================================================================
Concepts taught in this file:
1. What is an API & Microservice architecture?
2. FastAPI framework: routes, dependency injection, and ASGI.
3. Strict request/response validation with Pydantic.
4. Exposing AI capabilities over HTTP for our future Express TypeScript server.
5. Interactive API documentation with Swagger UI (/docs).
=============================================================================
"""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import our Day 2 and Day 3 core AI logic
from day2_curriculum import get_curriculum, CurriculumSchema
from day3_step_tutor import call_llm, TEACHER_SYSTEM_PROMPT

load_dotenv()

# =============================================================================
# 1. INITIALIZE FASTAPI APPLICATION
# =============================================================================
app = FastAPI(
    title="AI Notebook — AI Brain Service",
    description="Dedicated Python microservice powering LLM curriculum generation, step-by-step tutoring, and doubt resolution.",
    version="1.0.0",
)

# Enable CORS so our future Express backend (and frontend) can communicate without browser blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# 2. DEFINE REQUEST & RESPONSE SCHEMAS
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class GenerateCurriculumRequest(BaseModel):
    subject: str = Field(..., example="React Hooks", description="The subject or skill to learn")
    level: Optional[str] = Field("Beginner to Advanced", example="Beginner to Advanced")


class TeachLessonRequest(BaseModel):
    subject: str = Field(..., example="React Mastery")
    module_title: str = Field(..., example="Hooks Fundamentals")
    lesson_title: str = Field(..., example="Understanding useEffect")
    lesson_description: Optional[str] = Field("", example="Learn why useEffect exists and how dependencies work.")
    key_concepts: Optional[List[str]] = Field(default_factory=list, example=["Side effects", "Dependency array", "Cleanup"])


class TeachLessonResponse(BaseModel):
    subject: str
    module_title: str
    lesson_title: str
    explanation: str


class AnswerDoubtRequest(BaseModel):
    subject: str = Field(..., example="React Mastery")
    module_title: str = Field(..., example="Hooks Fundamentals")
    lesson_title: str = Field(..., example="Understanding useEffect")
    current_lesson_text: str = Field(..., description="The explanation text of the lesson being studied")
    doubt: str = Field(..., example="Does cleanup run every time the component re-renders?")


class AnswerDoubtResponse(BaseModel):
    lesson_title: str
    doubt: str
    answer: str
    status: str = "answered"


# =============================================================================
# 3. API ENDPOINTS
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint to verify the AI microservice is alive."""
    return {
        "status": "healthy",
        "service": "ai-notebook-brain",
        "version": "1.0.0"
    }


@app.post("/ai/generate-curriculum", response_model=CurriculumSchema, tags=["Curriculum"])
def api_generate_curriculum(payload: GenerateCurriculumRequest):
    """
    Generates a complete, structured multi-module curriculum in strict JSON format.
    Called by our Express backend when a user creates a new notebook.
    """
    try:
        curriculum = get_curriculum(payload.subject)
        return curriculum
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate curriculum: {str(e)}")


@app.post("/ai/teach-lesson", response_model=TeachLessonResponse, tags=["Tutor"])
def api_teach_lesson(payload: TeachLessonRequest):
    """
    Delivers a comprehensive, step-by-step lesson explanation for a specific module & lesson.
    """
    try:
        prompt = (
            f"Please teach the following lesson now:\n"
            f"Subject: {payload.subject}\n"
            f"Module: {payload.module_title}\n"
            f"Lesson: {payload.lesson_title}\n"
            f"Goal: {payload.lesson_description}\n"
            f"Key Concepts: {', '.join(payload.key_concepts)}"
        )

        messages = [{"role": "user", "content": prompt}]
        explanation = call_llm(messages, temperature=0.4)

        return TeachLessonResponse(
            subject=payload.subject,
            module_title=payload.module_title,
            lesson_title=payload.lesson_title,
            explanation=explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to teach lesson: {str(e)}")


@app.post("/ai/answer-doubt", response_model=AnswerDoubtResponse, tags=["Tutor"])
def api_answer_doubt(payload: AnswerDoubtRequest):
    """
    Answers a student's doubt using the active lesson text as grounded context.
    """
    try:
        messages = [
            {
                "role": "user",
                "content": (
                    f"You are teaching {payload.subject} -> {payload.module_title} -> {payload.lesson_title}.\n"
                    f"Here is the lesson text previously taught:\n\"\"\"{payload.current_lesson_text}\"\"\"\n\n"
                    f"The student has this doubt: \"{payload.doubt}\"\n"
                    f"Explain the doubt clearly, addressing how it connects to the lesson."
                )
            }
        ]

        answer = call_llm(messages, temperature=0.5)

        return AnswerDoubtResponse(
            lesson_title=payload.lesson_title,
            doubt=payload.doubt,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer doubt: {str(e)}")


# =============================================================================
# 4. ENTRYPOINT RUNNER
# =============================================================================
if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting AI Notebook Python Microservice on http://localhost:8000")
    print("📖 Interactive API Docs available at http://localhost:8000/docs\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
