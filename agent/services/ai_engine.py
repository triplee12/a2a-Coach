import os
import httpx

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def call_gemini(prompt: str):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    data = {
        "contents": [{"parts":[{"text": prompt}]}]
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers=headers, params=params, json=data)

    result = response.json()
    return result["candidates"][0]["content"]["parts"][0]["text"]


async def coach_agent(user_message: str):
    prompt = f"""
You are a multi-modal smart coaching agent for learning & development.
User input: {user_message}

Your abilities include:
- teaching concepts (tech, business, self-growth, psychology)
- breaking down learning paths
- creating SMART goals
- motivational support and confidence boost
- structured learning plans & habits
- multi-topic reasoning (not limited to any field)

Return clear, actionable insight.
"""

    return await call_gemini(prompt)
