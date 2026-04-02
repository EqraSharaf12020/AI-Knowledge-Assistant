import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_legal_analysis(text_context):
    from rag.prompts import LEGAL_SYSTEM_PROMPT
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze this contract: {text_context[:8000]}"}
        ],
        response_format={"type": "json_object"}
    )
    return completion.choices[0].message.content