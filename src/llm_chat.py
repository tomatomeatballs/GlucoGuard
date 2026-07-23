from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("API_KEY")
)


def ask_llm(question, glucose_context="", system_prompt=None, max_tokens=500):

    if system_prompt is None:
        system_prompt = (
            "You are GlucoGuard AI Health Assistant, a professional diabetes education specialist. "
            "You explain glucose trends clearly, give practical lifestyle recommendations, "
            "and help users understand their predicted glucose trajectory. "
            "You do NOT provide medical diagnoses or replace a doctor's advice. "
            "Always include a disclaimer when giving health suggestions."
        )

    prompt = f"""
Glucose data context:
{glucose_context}

User question / request:
{question}

Please provide a thorough, structured response. If predictions are included, explain the likely trajectory. If lifestyle factors (insulin, food, exercise) are mentioned, explain how they would affect the predicted glucose values and suggest adjustments.
"""

    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content