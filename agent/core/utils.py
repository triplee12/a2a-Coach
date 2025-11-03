import hmac
import hashlib
import time
from agent.core.logger import logger


def verify_a2a_signature(body_bytes: bytes, timestamp: str, signature: str, secret: str, tolerance_sec: int = 300) -> bool:
    """
    Verify HMAC-SHA256 signature.

    Expected signature format: hex-encoded HMAC of (timestamp + body) using shared secret.
    Headers expected from Telex:
    X-A2A-Signature: <hex-hmac>
    X-A2A-Timestamp: <unix-timestamp>

    This function checks timestamp tolerance to prevent replay attacks.
    """
    logger.info({"event": "verifying_signature", "timestamp": timestamp, "signature": signature})
    if not secret:
        return False

    try:
        ts = int(timestamp)
    except Exception as e:
        logger.exception(e)
        return False

    now = int(time.time())
    if abs(now - ts) > tolerance_sec:
        return False

    msg = timestamp.encode("utf-8") + body_bytes
    expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected, signature)


def short_plan_from_prompt(user_text: str) -> str:
    text = user_text.lower()
    if any(k in text for k in ("learn", "plan", "study", "teach", "coach", "help")):
        return (
        f"Quick 4-week plan for: {user_text}\n\n"
        "Week 1 — Foundations: core concepts and simple exercises.\n"
        "Week 2 — Tools & Practice: apply libraries / key tools.\n"
        "Week 3 — Mini Projects: build a small project for practice.\n"
        "Week 4 — Polish & Showcase: finish project and document it.\n\n"
        "Next step: pick a 1-hour exercise to complete today."
        )
    return f"I can help with that: {user_text}\n\nNext step: tell me the exact outcome you want and your timeline (e.g., 'Become job-ready in 3 months')."
