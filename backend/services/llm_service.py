
from rag.prompts import LEGAL_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client with a backend timeout so slow model responses do not hang forever.
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=float(os.getenv("GROQ_TIMEOUT", "120")),
    base_url=os.getenv("GROQ_BASE_URL", None),
)

MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def get_legal_analysis(document_text: str):
    """
    Analyzes a legal document and returns a structured JSON risks object.
    Uses LEGAL_SYSTEM_PROMPT to instruct the model to return { "risks": [...] }.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": LEGAL_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"Analyze this legal document and return ONLY a JSON object:\n\n{document_text}",
                }
            ],
            model=MODEL_NAME,
            temperature=0.1,  # Very low for consistent structured output
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ Groq API Error (analysis): {str(e)}")
        return f"Error: {str(e)}"


def get_chat_answer(rag_prompt: str):
    """
    Answers a user question using RAG context.
    Uses CHAT_SYSTEM_PROMPT so the model behaves like a legal assistant.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": CHAT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": rag_prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"❌ Groq API Error (chat): {str(e)}")
        return f"Error: {str(e)}"