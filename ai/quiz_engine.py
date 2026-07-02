import os
from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_quiz(topic, explanation):

    prompt = f"""
Create a quiz from the following lesson.

Topic:
{topic}

Lesson:
{explanation}

Rules:

Generate exactly 5 MCQs.

Each question should have

A)
B)
C)
D)

After all questions,

provide the correct answers separately.

Do not explain the answers.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.5
        )
    )

    return response.text