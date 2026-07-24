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


# [KYLE] 2026-07-24 -- added alongside ask_llm(), not replacing it. ask_llm() builds a
# single one-shot prompt with a hardcoded instruction baked in ("explain the trajectory,
# explain lifestyle factors...") -- great for the first full analysis, but it means every
# follow-up question got a full re-explanation bolted on, because that instruction fires
# again no matter what. Real chat APIs support passing the WHOLE conversation so far as a
# list of turns; the model then naturally treats a follow-up as a follow-up (short,
# on-topic) instead of a fresh "write a report" request each time. That's what this does.
def ask_llm_chat(messages, max_tokens=500):
    """
    Multi-turn chat completion. `messages` is the full conversation so far, in the
    standard OpenAI chat format:
        [{"role": "system", "content": "..."},
         {"role": "user", "content": "..."},
         {"role": "assistant", "content": "..."},
         {"role": "user", "content": "..."}, ...]
    No extra instructions are injected here -- the caller (app.py) controls the entire
    conversation, including the system prompt as messages[0]. Returns just the new
    reply text; the caller is responsible for appending it back onto `messages` to keep
    the conversation going.
    """
    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=messages,
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content