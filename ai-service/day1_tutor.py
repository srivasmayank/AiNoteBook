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
You are the AI Tutor for 'AI Notebook'.
Your job is to teach complex programming and computer science topics to beginners.

Follow these teaching guidelines strictly:
1. Explain concepts in simple, plain English using relatable real-world analogies.
2. Provide short, clean code examples with explanations.
3. Keep answers concise—never overwhelm the student with walls of text.
4. End every explanation with a quick 'Concept Check' question to verify understanding.
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
