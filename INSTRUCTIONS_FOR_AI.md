# Instructions for AI (Claude Code / any coding assistant)

The user is a newly-certified **AI Integraterz AI Integrator**. Walk them through setting up this Autonomous Job Agent in plain English. Do NOT assume coding skill.

Follow these steps in order. Run commands for them — don't just list them.

---

## 1. Check Python

Run: `python --version`

- If 3.10 or newer → continue.
- If older than 3.10 → tell them to install Python 3.12 from https://www.python.org/downloads/ (select "Add Python to PATH" during install).
- If 3.14 → warn them it works but 3.12 is smoother. Continue.

## 2. Create virtual environment and install deps

In the repo root:

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac (zsh/bash):**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If `pip install` fails with SSL / network errors → retry once. Common on corporate Wi-Fi.

## 3. Run the setup wizard — hand-hold them

```
python setup.py
```

For each question, ask the user conversationally in chat, then type their answer into the wizard. Questions:

- **Full name** → for their application signature.
- **Calendar link** → Calendly or similar. If they don't have one, point them to https://calendly.com (free).
- **Portfolio link** → their Operations Agent Loom from certification, or a GitHub / any public demo. If they don't have one yet, they can paste a placeholder and update `config.json` later.
- **Niches** → 1-3 from the Grad Playbook starter list (insurance brokerages, medical practices, law firms, real estate teams, etc.). Don't all pick the same ones.
- **Keywords** → defaults are good ("AI Integrator, AI automation, virtual assistant, operations automation"). Add niche-specific ones if they have a clear target (e.g., "insurance automation" if niche is insurance brokerages).
- **Drafts per platform** → default 10 is fine.
- **Gemini API key** → send them to https://aistudio.google.com/apikey. Free. Click "Create API Key" → Default project → copy the string. New keys may NOT start with `AIza` — don't reject unusual formats.

The wizard validates the key with a live call. If it fails, re-prompt once.

## 4. Smoke test (no browser visible)

```
python run.py --smoke-test
```

Should finish in under a minute. Produces `upwork_drafts.csv`, `onlinejobs_drafts.csv`, `daily_drafts.csv` with stub application text. If this works, the plumbing is correct.

## 5. First real run

```
python run.py
```

- A Chrome window opens. It's a **separate profile** (inside `user_data/`) — not the user's personal Chrome.
- On first run for each platform, the script detects the login page and waits 90 seconds. Tell the user: "Log in manually in the Chrome window — you have 90 seconds."
- After login, cookies persist. Subsequent runs skip login.
- When done, open `daily_drafts.csv` (Excel, Google Sheets, or any viewer).

## 6. Walk them through one draft

Open `daily_drafts.csv`, pick the first row, and show them:
- The `application_text` column is the copy-paste-ready draft.
- It already encodes the Grad Playbook's 7-item audit rubric (personalization, embedded-team-member positioning, certification + mastermind + portfolio mention, low-pressure CTA, under 180 words).
- They should still proofread — Gemini occasionally gets a detail wrong.

## 7. Suggest extensions (learning nudges, don't build)

- Auto-submit the top pick after marking a "submit?" column.
- Push daily_drafts.csv to a Google Sheet via `gspread`.
- Add Freelancer.com (copy `scrapers/upwork.py`, change URL + selectors).
- Schedule daily runs via Windows Task Scheduler / macOS `cron`.

---

## Common issues

| Symptom | Fix |
|---|---|
| `ChromeDriver` / version mismatch | `pip install --upgrade webdriver-manager` then retry. |
| Gemini "404 model not found" | Make sure the key is from Google AI Studio, not Vertex. |
| Chrome opens then immediately closes | Close all other Chrome windows using the same profile, retry. |
| CSV looks garbled in Excel | Open it in Google Sheets instead, or re-import with UTF-8. |
| 0 jobs extracted on a platform | Site changed DOM — edit the `CARD_SELECTORS` list in the matching `scrapers/*.py`. |
