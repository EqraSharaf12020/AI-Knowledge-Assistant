
from rag.prompts import LEGAL_SYSTEM_PROMPT

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_legal_analysis(prompt: str):
    """
    Sends the legal prompt to Llama 3.3 and returns a CLEAN string.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Use the stable Llama model
            temperature=0.3, # Low temperature for factual legal answers
        )
        
        # EXTRACT THE TEXT: This is the critical part
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ Groq API Error: {str(e)}")
        return f"Error: {str(e)}"