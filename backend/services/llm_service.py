import os
from groq import Groq
from dotenv import load_dotenv
from rag.prompts import LEGAL_SYSTEM_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

import json

def get_legal_analysis(text_content: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this contract: {text_content[:8000]}"}
            ],
            response_format={"type": "json_object"} # Tells Groq to send JSON
        )
        
        # Get the raw text from the AI
        raw_response = completion.choices[0].message.content
        
        # This is the magic line: it turns the string into a dictionary
        return json.loads(raw_response)
        
    except Exception as e:
        print(f"Error: {e}")
        return {"risks": []}