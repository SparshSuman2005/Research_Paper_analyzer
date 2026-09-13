from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

def generate_answer(question,context):

    prompt = f"""
        You are a research paper assistant.

        Answer the user's question using only the information
        provided in the context.

        If the answer cannot be found in the context,
        say that the answer cannot be found in the provided
        paper content.

        Do not make up information.

        Question:
        {question}

        Context:
        {context}

        Give a clear and concise answer.
        """

    response=client.models.generate_content(
          model="gemini-2.5-flash",
          contents=prompt
     )
    return response.text