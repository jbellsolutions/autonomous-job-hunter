"""Interactive first-run setup wizard.

Collects grad profile, validates Gemini API key, writes .env and config.json.
Run: python setup.py
"""
import json
import os
import sys
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent
ENV_PATH = REPO_ROOT / ".env"
CONFIG_PATH = REPO_ROOT / "config.json"

DEFAULT_KEYWORDS = [
    "AI Integrator",
    "AI automation",
    "virtual assistant",
    "operations automation",
]


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val or default


def ask_list(prompt: str, default: list) -> list:
    default_str = ", ".join(default)
    raw = ask(prompt, default_str)
    return [x.strip() for x in raw.split(",") if x.strip()]


def main():
    print("=" * 60)
    print("  AI Integraterz Autonomous Job Agent — Setup Wizard")
    print("=" * 60)

    # Python version check
    if sys.version_info < (3, 10):
        print(f"\nERROR: Python 3.10+ required. You have {sys.version.split()[0]}.")
        sys.exit(1)
    if sys.version_info >= (3, 14):
        print(
            f"\nWARNING: You are on Python {sys.version.split()[0]}. "
            "Python 3.12 is recommended. Continuing anyway.\n"
        )

    # Existing config?
    if ENV_PATH.exists() and CONFIG_PATH.exists():
        ans = ask("Config already exists. Overwrite? (y/N)", "N")
        if ans.lower() != "y":
            print("Keeping existing config. Exiting.")
            return

    existing = {}
    if CONFIG_PATH.exists():
        try:
            existing = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    print("\nTell me about you (this goes into every application signature):\n")

    grad_name = ask("Your full name", existing.get("grad_name", ""))
    calendar_link = ask("Your Calendly / calendar link", existing.get("calendar_link", ""))
    portfolio_link = ask(
        "Link to your portfolio or Operations Agent Loom",
        existing.get("portfolio_link", ""),
    )

    print("\nTarget niches (from the Grad Playbook list — comma-separated, 1-3 max):")
    niches = ask_list("Niches", existing.get("niches", []))

    print("\nJob keywords to search for (comma-separated):")
    keywords = ask_list("Keywords", existing.get("keywords", DEFAULT_KEYWORDS))

    drafts_per_run_str = ask(
        "How many drafts per platform per run?",
        str(existing.get("drafts_per_run", 10)),
    )
    try:
        drafts_per_run = max(1, int(drafts_per_run_str))
    except ValueError:
        drafts_per_run = 10

    # Gemini API key
    print("\nGemini API key (free at https://aistudio.google.com/apikey):")
    print("Note: new keys may not start with 'AIza' — paste whatever Google gave you.")

    existing_key = ""
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("GOOGLE_API_KEY="):
                existing_key = line.split("=", 1)[1].strip()
                break

    api_key = ask("Gemini API key", existing_key)

    # Validate key
    if api_key:
        print("\nValidating key with a live Gemini call...")
        try:
            from scrapers.gemini import validate_api_key
            ok, msg = validate_api_key(api_key)
            if ok:
                print("  ✓ Gemini key works.")
            else:
                print(f"  ! Key validation failed: {msg}")
                retry = ask("Re-enter key? (y/N)", "N")
                if retry.lower() == "y":
                    api_key = ask("Gemini API key", "")
        except Exception as e:
            print(f"  ! Could not validate (will save anyway): {e}")

    # Write .env
    ENV_PATH.write_text(f"GOOGLE_API_KEY={api_key}\n", encoding="utf-8")
    print(f"\n  ✓ Wrote {ENV_PATH.name}")

    # Write config.json
    config = {
        "grad_name": grad_name,
        "calendar_link": calendar_link,
        "portfolio_link": portfolio_link,
        "niches": niches,
        "keywords": keywords or DEFAULT_KEYWORDS,
        "drafts_per_run": drafts_per_run,
        "start_date": existing.get("start_date", date.today().isoformat()),
    }
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"  ✓ Wrote {CONFIG_PATH.name}")

    print("\n" + "=" * 60)
    print("  Setup complete. Next step:")
    print("     python run.py")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
