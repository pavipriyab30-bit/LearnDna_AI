import os
from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_explanation(topic, style, difficulty, language):

    prompt = f"""
You are LearnDNA AI.

Teach ONLY the following topic.

Topic:
{topic}

Student Preference:
Learning Style : {style}
Difficulty : {difficulty}
Language : {language}

Instructions:

- Explain according to the selected learning style.
- Keep the explanation simple.
- Use headings.
- Give examples.
- Finish with a short summary.
- Do NOT generate quiz questions.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7
        )
    )

    return response.text