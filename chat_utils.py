# utils/chat_utils.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_openai(message, language="en"):
    """Ask the OpenAI model (GPT-4 or GPT-3.5) for an answer."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or gpt-4o if you have access
            messages=[
                {"role": "system", "content": f"You are an AI assistant that replies in {language}."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with AI: {e}"
