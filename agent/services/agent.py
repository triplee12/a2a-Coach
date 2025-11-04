import google.generativeai as genai
from agent.core.config import GEMINI_API_KEY
from agent.core.logger import logger
from agent.core.utils import short_plan_from_prompt

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a smart multi-modal learning & productivity AI coach.

Capabilities:
- Help users learn skills, plan study routines & build habits
- Break complex topics into simple steps
- Provide motivation, accountability & actionable advice
- Help with coding, research, communication & personal growth
- Ask clarifying questions when needed
- Keep responses concise but helpful

Format:
- If answering: Give clear guidance
- If user unclear: Ask friendly follow-up questions
- ALWAYS provide next-step suggestions
"""


def run_gemini(user_text: str) -> str:
    if not GEMINI_API_KEY:
        return short_plan_from_prompt(user_text)

    try:
        genai.configure(api_key=GEMINI_API_KEY)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"{SYSTEM_PROMPT}\nUser: {user_text}"
        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            return response.text.strip()

        return str(response).strip()

    except Exception as e:
        logger.exception(e)
        return short_plan_from_prompt(user_text) + "\n\n(LLM unavailable — served fallback)"
