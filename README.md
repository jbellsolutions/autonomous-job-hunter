# AI Integraterz Autonomous Job Agent

The Autonomous Job Agent from your AI Integraterz certification. Pulls recent AI Integrator / automation jobs from **Upwork** and **OnlineJobs.ph**, drafts an AI Integraterz-aligned application for each, and saves them to CSV for your morning review.

It does **not** auto-submit anything. You review 5-10 drafts, tweak if needed, and submit by hand — same rhythm as Part 6 of the Grad Playbook.

---

## Quick setup — the easy way

1. Open this folder in Claude Code (or any coding assistant).
2. Say: **"Read INSTRUCTIONS_FOR_AI.md and set this up for me."**
3. Answer Claude's questions in plain English. Claude runs every command for you.

That's it. Skip the rest of this README.

---

## Manual setup — if you'd rather type commands

**Requirements:** Python 3.10+ (3.12 recommended), a free Gemini API key from https://aistudio.google.com/apikey, and Chrome installed.

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python setup.py
python run.py
```

### Mac (Terminal)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py
python run.py
```

First time you run `python run.py`, a Chrome window opens. Log in to Upwork and OnlineJobs.ph manually — you have 90 seconds per site. Cookies save to `user_data/` so you never log in again.

Output: `daily_drafts.csv` in the repo root. Open it in Excel, Google Sheets, or Numbers.

---

## What to do each morning

1. `python run.py`
2. Open `daily_drafts.csv`.
3. Review each row's `application_text`. Tweak any shaky research line.
4. Submit 5-10 of the good ones on the platform.
5. Log submissions in your tracking sheet.
6. Post your daily numbers in Skool — the script prints a copy-paste-ready line.

---

## Extend it (your learning project)

Ideas worth trying — each teaches you something new:

1. **Auto-submit flagged picks.** Add a `submit?` column to the CSV. Write a small script that reads rows marked "yes" and submits them on the platform.
2. **Push to Google Sheets.** Replace the CSV write with `gspread`. Collect the sheet URL in `setup.py`.
3. **Add Freelancer.com.** Copy `scrapers/upwork.py`, change the URL + card selectors, wire it into `run.py`.
4. **Schedule it.** Windows Task Scheduler (macOS: `cron`) to run `python run.py` every morning at 7am.
5. **Post to Skool automatically.** Use Skool's API (or Selenium) to drop the daily-numbers summary into `#grad-daily-standup`.

Each of these is a small, self-contained improvement. Fork the repo, ship one, show it off in Skool.

---

## Troubleshooting

See the bottom of [INSTRUCTIONS_FOR_AI.md](INSTRUCTIONS_FOR_AI.md) for the common-issues table.
