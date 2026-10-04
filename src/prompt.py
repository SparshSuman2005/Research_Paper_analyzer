from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-pro-latest",
    "gemini-3-flash-preview",
]

def generate_answer(question, context):
    prompt = f"""You are an expert academic research paper assistant.

Answer the user's question accurately, clearly, and concisely using ONLY the information provided in the context below.

Rules:
1. Base your answer strictly on the provided Context.
2. If the answer cannot be found in the context, explicitly state: "The answer cannot be found in the provided paper content."
3. Do NOT hallucinate or extrapolate beyond what the research text affirms.
4. When relevant, cite the specific paper or source section referenced.

Question:
{question}

Context:
{context}

Answer:"""

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")