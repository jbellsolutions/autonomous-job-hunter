import os
import time
from pathlib import Path

import google.generativeai as genai

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "ai_integraterz_outreach.txt"
SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

MODEL_NAME = "gemini-2.5-flash"


def _fallback(job_title: str, config: dict) -> str:
    name = config.get("grad_name", "[Your Name]")
    cal = config.get("calendar_link", "[Calendar Link]")
    port = config.get("portfolio_link", "[Portfolio Link]")
    return (
        f"Hi,\n\n"
        f"I noticed your posting for {job_title} and wanted to reach out. "
        f"I'm a certified AI Integrator — trained through a US-based program with "
        f"mastermind support and a portfolio requirement. I help small teams embed AI "
        f"as part of daily ops, not as a vendor or freelancer, but as an embedded team member.\n\n"
        f"If you're open to it, I'd love 15 minutes to learn more about the bottlenecks "
        f"you're trying to solve. If I'm not the fit, I may know a teammate from my program who is.\n\n"
        f"{name}\n"
        f"Certified AI Integrator | AI Integraterz Program\n"
        f"{cal}\n"
        f"{port}\n"
    )


def generate_application(job_title: str, job_description: str, config: dict) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return _fallback(job_title, config)

    niches = ", ".join(config.get("niches", [])) or "(none specified)"
    user_message = (
        f"JOB TITLE: {job_title}\n"
        f"JOB DESCRIPTION:\n{job_description}\n\n"
        f"GRAD PROFILE:\n"
        f"Name: {config.get('grad_name', '')}\n"
        f"Calendar: {config.get('calendar_link', '')}\n"
        f"Portfolio: {config.get('portfolio_link', '')}\n"
        f"Target niches: {niches}\n"
    )

    for attempt in range(2):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(user_message)
            text = (response.text or "").strip()
            if text:
                return text
        except Exception as e:
            if attempt == 0:
                time.sleep(3)
                continue
            print(f"  ! Gemini failed twice: {e}. Using fallback.")
    return _fallback(job_title, config)


def validate_api_key(api_key: str) -> tuple[bool, str]:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        r = model.generate_content("Say hi in 3 words.")
        if r.text:
            return True, "ok"
        return False, "empty response"
    except Exception as e:
        return False, str(e)
