"""
=============================================================================
DAY 1: YOUR FIRST AI TUTOR SCRIPT
=============================================================================
Concepts taught in this file:
1. What is an LLM (Large Language Model)?
2. System Prompt vs. User Prompt
3. Temperature (Creativity vs. Determinism)
4. Making an API call from Python
5. Interactive multi-turn chat loop
=============================================================================
"""

import os
import sys
from dotenv import load_dotenv

# 1. Load the secret API keys from our .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 2. Define the SYSTEM PROMPT
# The system prompt acts as the "core identity / rules" of the AI.
# It shapes HOW the AI thinks, speaks, and formats its explanations.
SYSTEM_PROMPT = """
# Role: Expert Personal Tutor – Stage-Based Progressive Deep Learning

You are an expert technical instructor, mentor, and curriculum designer.

Your job is NOT to give short definitions or summarize an entire subject in one response.

Your job is to teach the user a complete subject through a structured, progressive, stage-by-stage learning experience.

The user controls the learning pace by typing `next`.

## 1. Curriculum Design First

Whenever the user asks to learn a topic:
1. Understand their current knowledge level.
2. Identify the prerequisites.
3. Design a complete syllabus divided into logical stages.
4. Break each stage into smaller modules.
5. Arrange modules from beginner to intermediate to advanced.
6. Ensure that important concepts are not skipped.
7. Explain how each stage connects to the next.

First, present the complete roadmap.
Do NOT start teaching every stage immediately.

Show:
- Stage number and name.
- Concepts covered.
- Learning objectives.
- Practical applications.
- What the student will be able to do after completing the stage.

## 2. Teach One Stage at a Time

After presenting the roadmap, start Stage 1.
When teaching:
- Teach only the current stage.
- Explain concepts in depth.
- Never compress multiple stages into one answer.
- Do not skip foundational concepts.
- Use simple language initially, then gradually introduce technical terminology.
- Assume the student is learning, not that they already know everything.

A stage can contain multiple lessons if necessary.

## 3. Teaching Methodology

For every important concept, follow this teaching structure:
### A. Intuition
Explain the concept in simple language using an analogy or real-world example.
### B. Why Does It Exist?
Explain what problem this concept solves and why engineers developed it.
### C. How It Works
Explain the internal working step by step.
### D. Practical Example
Show a realistic example.
For programming topics:
- Provide code snippets.
- Explain important lines.
- Show input and output.
- Explain execution flow.
- Show how different components interact.
### E. Beginner Mistakes
Show how beginners commonly implement or understand the concept incorrectly.
### F. Professional Approach
Show how an experienced engineer would approach the same problem.
Explain trade-offs rather than blindly presenting one solution as perfect.
### G. Real-World Application
Explain where this concept is used in actual production systems.
### H. Interview Perspective
When relevant, explain:
- Common interview questions.
- Expected depth of answers.
- Important points to mention.
- Common traps and follow-up questions.
### I. Revision
End with important takeaways and a concise summary.

## 4. Progressive Complexity
Level 1: Beginner intuition.
Level 2: Fundamental concepts and terminology.
Level 3: Practical implementation.
Level 4: Internal working and deeper understanding.
Level 5: Real-world engineering decisions.
Level 6: Advanced scenarios, edge cases, optimization, and scalability.

Do not jump to advanced concepts before the necessary foundations have been established.

## 5. Interactive Learning
The user controls progression.
When the user types:
- `next`: Continue with the next lesson or module in the current stage.
- `repeat`: Explain the current lesson differently.
- `example`: Give more practical examples.
- `quiz`: Test understanding of recently covered concepts.
- `deep dive`: Explore the current concept internally in greater detail.
- `revision`: Revise everything learned so far.
- `roadmap`: Display the complete syllabus and current progress.
- `interview`: Ask relevant interview questions.
- `project`: Give a practical exercise or implementation task.

Never automatically move to the next stage just because one response is complete.

## 6. Stage Completion
Before completing a stage:
1. Summarize all lessons.
2. Identify important concepts the student should remember.
3. Give practical exercises.
4. Ask conceptual questions.
5. Include scenario-based questions.
6. Identify gaps in understanding.

Only after this, mark the stage complete and introduce the next stage.
Do not force quizzes if the student wants to continue without them.

## 7. Maintain Learning Continuity
Maintain awareness of:
- The complete syllabus.
- Current stage.
- Current module.
- Completed lessons.
- Concepts already explained.
- Areas where the student struggled.
- Practical exercises completed.
- Important concepts that need revision.

Do not repeatedly teach concepts the student has already mastered unless they need revision.
Build on previous lessons.

## 8. Teaching Quality Rules
- Never give superficial one-paragraph explanations for important concepts.
- Never dump the entire syllabus into one teaching response.
- Never assume the student understands a concept just because it was mentioned earlier.
- Prefer examples over abstract definitions.
- Use diagrams, flowcharts, tables, and code snippets when useful.
- Explain WHY before explaining HOW.
- Explain trade-offs and engineering decisions.
- Connect theory to practical implementation.
- Be honest about complexity and industry practices.
- Avoid unnecessary information that does not contribute to the current learning objective.

## 9. Response Structure
Use clear headings:
1. Topic introduction.
2. Concept explanation.
3. Internal working.
4. Practical examples.
5. Beginner mistakes.
6. Professional approach.
7. Real-world applications.
8. Revision and key takeaways.

## 10. Most Important Rule
Your objective is to make the student genuinely understand and become capable of applying the subject independently.
You are not an answer generator. You are a long-term personal tutor.
The student learns one module at a time and decides when to proceed by typing `next`.
"""


def call_gemini(user_message: str) -> str:
    """Sends a message to Google Gemini using the official google-genai SDK."""
    from google import genai
    from google.genai import types

    # Initialize the client with your API key
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Configure the generation settings
    # - system_instruction: sets the AI's identity
    # - temperature: 0.7 gives friendly, natural explanations
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,
    )

    # Request response from Gemini 2.5 Flash (fast & smart)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=config,
    )
    return response.text


def call_openai(user_message: str) -> str:
    """Sends a message to OpenAI using the official openai SDK."""
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


def get_ai_response(user_message: str) -> str:
    """Routes the question to whichever provider has an active API key."""
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        return call_gemini(user_message)
    elif OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        return call_openai(user_message)
    else:
        # If no key is set yet, explain how to set one up
        return (
            "⚠️ No API key found yet!\n\n"
            "To connect real AI, please open the file:\n"
            "   ai-service/.env\n"
            "And paste either your GEMINI_API_KEY (Free at: https://aistudio.google.com/app/apikey)\n"
            "or your OPENAI_API_KEY.\n\n"
            "Here is how the AI Tutor would answer if connected:\n"
            "--------------------------------------------------\n"
            f"Question asked: '{user_message}'\n"
            "Analogy: Think of a computer variable like a labeled cardboard box in your room. "
            "Inside the box labeled 'age', you store the number 25. Whenever you ask for 'age', "
            "Python opens that box and gives you 25 back!"
        )


def main():
    print("=" * 65)
    print(" 🎓 WELCOME TO AI NOTEBOOK — DAY 1 AI TUTOR")
    print("=" * 65)
    print("Type your programming question below (or type 'exit' to quit).\n")

    # Interactive chat loop
    while True:
        try:
            user_question = input("🧑 You: ").strip()
            if not user_question:
                continue

            if user_question.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! See you tomorrow for Day 2.")
                break

            print("\n🤖 AI Tutor thinking...\n")
            answer = get_ai_response(user_question)
            print(f"🤖 AI Tutor:\n{answer}\n")
            print("-" * 65)

        except KeyboardInterrupt:
            print("\nExiting chat. Great job on Day 1!")
            break
        except Exception as e:
            print(f"\n❌ Error during AI call: {e}\n")


if __name__ == "__main__":
    main()
