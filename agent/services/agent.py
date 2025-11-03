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


# def run_gemini_agent(user_message: str) -> str:
#     logger.info({"event": "message_received", "message": user_message})
#     try:
#         model = genai.GenerativeModel("gemini-pro")
#         response = model.generate_content(f"{SYSTEM_PROMPT}\nUser: {user_message}")
#         return response.text.strip()
#     except Exception as e:
#         logger.exception(e)
#         return "I'm having trouble thinking right now. Try again!"


def run_gemini(user_text: str) -> str:
    if not GEMINI_API_KEY:
        return short_plan_from_prompt(user_text)

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(contents=f"{SYSTEM_PROMPT}\nUser: {user_text}")
        text = ""
        if hasattr(response, "candidates"):
            text = response.candidates[0].content
        elif isinstance(response, dict) and "output" in response:
            text = response["output"][0]["content"][0]["text"]
        else:
            text = str(response)
        return text.strip()
    except Exception as e:
        logger.exception(e)
        return short_plan_from_prompt(user_text) + "\n\n(LLM unavailable — served fallback)"
