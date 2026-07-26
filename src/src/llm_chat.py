from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from dotenv import load_dotenv
import os

load_dotenv()

_API_KEY = os.getenv("API_KEY")

if not _API_KEY:
    raise RuntimeError(
        "API_KEY not found in environment variables. "
        "Please set it in your .env file or export it before launching the app."
    )

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=_API_KEY
)


# Shared error handling for both ask_llm() and ask_llm_chat() below -- same failure
# modes apply to either call (bad key, rate limit, network, malformed response), so both
# funnel through this instead of duplicating the try/except twice.
def _call_chat_api(messages, max_tokens):
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=messages,
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except AuthenticationError:
        return (
            "⚠️ **LLM service unavailable** — API authentication failed. "
            "Please contact the administrator to verify the API key."
        )
    except RateLimitError:
        return (
            "⚠️ **LLM service busy** — request rate limit exceeded. "
            "Please wait a moment and try again."
        )
    except APIConnectionError:
        return (
            "⚠️ **LLM service unreachable** — could not connect to the NVIDIA API. "
            "Please check your internet connection and try again."
        )
    except APIError as e:
        return (
            f"⚠️ **LLM service error** — the API returned an unexpected error. "
            f"Details: {e}"
        )
    except (KeyError, IndexError, AttributeError):
        return (
            "⚠️ **LLM response error** — the API returned an unexpected response format. "
            "Please try again or contact the administrator."
        )
    except Exception as e:
        return (
            f"⚠️ **Unexpected error** — an unknown issue occurred while contacting the LLM. "
            f"Details: {e}"
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

    return _call_chat_api(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens,
    )


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
    return _call_chat_api(messages, max_tokens)