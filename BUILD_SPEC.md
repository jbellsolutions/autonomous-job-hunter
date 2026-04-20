# BUILD SPEC — AI Integraterz Autonomous Job Agent v3

**Purpose of this file:** Paste this into a fresh Claude Code session (or any coding AI) with the instruction "Build this exactly as specified." It is self-contained — no prior conversation needed.

---

## 1. What you are building

A Python CLI tool that:
1. Opens a Chrome browser window (using Selenium, not Playwright).
2. Scrapes recent job postings from **Upwork** and **OnlineJobs.ph** matching user-supplied keywords (e.g., "AI Integrator", "AI automation").
3. For each post, calls **Google Gemini 2.5 Flash** (free tier) to draft a personalized application in the voice of a AI Integraterz-certified AI Integrator.
4. Writes all drafts to a CSV the user reviews in the morning, picks 5–10, and submits manually.
5. **Never auto-submits or auto-sends anything.** Read-only browsing + draft-writing only.

Audience: newly-certified AI Integraterz graduates on Windows (mostly) or Mac, with minimal coding skill. It must work on first run.

---

## 2. Hard constraints

- **Python 3.12 recommended.** Warn user if they're on 3.14+ (known Selenium asyncio issues on Windows — but Selenium itself is synchronous, so we avoid the root cause).
- **Cross-platform:** Windows + macOS. Linux nice-to-have.
- **Low resource:** single Chrome instance for the whole run, not one per platform.
- **Zero paid services.** Gemini free tier only. No OpenAI, no proxies, no CAPTCHA services.
- **No API keys in code.** Everything in `.env` (gitignored).
- **Read-only browser interactions.** Never click "Apply," "Submit," "Send," or equivalents.
- **No browser-use, no LangChain, no Playwright, no asyncio.** These caused the previous failure. Use plain Selenium + `webdriver-manager`.

---

## 3. Dependencies (pin in `requirements.txt`)

```
selenium>=4.20.0
webdriver-manager>=4.0.1
google-generativeai>=0.8.0
python-dotenv>=1.0.1
```

Nothing else. No `browser-use`, no `langchain-*`, no `playwright`.

---

## 4. Repo structure

```
autonomous-job-hunter/
├── README.md
├── INSTRUCTIONS_FOR_AI.md
├── BUILD_SPEC.md               # (this file, for reference)
├── requirements.txt
├── .env.example
├── .gitignore
├── setup.py                    # Interactive first-run wizard
├── run.py                      # Main entry point
├── prompts/
│   └── tenxva_outreach.txt     # LLM system prompt (see §9)
├── scrapers/
│   ├── __init__.py
│   ├── browser.py              # get_driver() — shared Chrome setup
│   ├── gemini.py               # generate_application()
│   ├── upwork.py
│   └── onlinejobs.py
└── user_data/                  # Chrome profile (auto-created, gitignored)
```

`.gitignore` must include: `.env`, `user_data/`, `*.csv`, `__pycache__/`, `venv/`, `*.pyc`, `config.json`.

---

## 5. Configuration files

### `.env`
```
GOOGLE_API_KEY=your_key_here
```

### `config.json` (written by `setup.py`)
```json
{
  "grad_name": "Jane Doe",
  "calendar_link": "https://calendly.com/jane-doe/15min",
  "portfolio_link": "https://loom.com/share/abc123",
  "niches": ["insurance brokerages", "dental practices"],
  "keywords": ["AI Integrator", "AI automation", "virtual assistant", "operations automation"],
  "drafts_per_run": 10,
  "start_date": "2026-04-18"
}
```

---

## 6. Module: `scrapers/browser.py`

One function, `get_driver(headless: bool = False) -> webdriver.Chrome`:

- Resolve repo root (two dirs up from this file).
- Profile path: `os.path.join(repo_root, "user_data")` — create if missing.
- Chrome options:
  - `--user-data-dir=<profile path>`
  - `--no-sandbox`
  - `--disable-dev-shm-usage`
  - `--disable-blink-features=AutomationControlled`
  - `excludeSwitches=["enable-automation"]`, `useAutomationExtension=False`
  - If `headless`: add `--headless=new` and `--window-size=1920,1080`.
- Driver: `webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)`.
- After creation: `driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")`.
- Implicit wait 5s, page load timeout 30s.
- Return the driver.

---

## 7. Module: `scrapers/gemini.py`

### `generate_application(job_title: str, job_description: str, config: dict) -> str`

- Read `prompts/tenxva_outreach.txt` once at module import.
- Build the user message:
  ```
  JOB TITLE: {job_title}
  JOB DESCRIPTION:
  {job_description}

  GRAD PROFILE:
  Name: {config["grad_name"]}
  Calendar: {config["calendar_link"]}
  Portfolio: {config["portfolio_link"]}
  Target niches: {", ".join(config["niches"])}
  ```
- Call `google.generativeai`:
  ```python
  genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
  model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=SYSTEM_PROMPT)
  response = model.generate_content(user_message)
  return response.text.strip()
  ```
- **Retry once** on any exception (wait 3s). On second failure, return a templated fallback (Template 1 from `tenxva_outreach.txt` with placeholders filled). Never raise — one bad job shouldn't break the run.

---

## 8. Platform scrapers — common contract

Each of `scrapers/upwork.py` and `scrapers/onlinejobs.py` exposes:

```python
def scrape(driver, config: dict, max_jobs: int = 5) -> list[dict]:
    """Returns list of dicts with keys:
       title, link, description, budget (or rate), posted_date (string, best-effort)
    """
```

Rules:
- Build the search URL from `config["keywords"]` joined as a query string (e.g., `"ai+automation"` on Upwork).
- `driver.get(search_url)`, wait up to 10s for listings to load.
- Scroll 3x (`window.scrollBy(0, 800)`, sleep 1.5s) to load lazy content.
- Use **multi-selector fallback**: try 3–5 CSS selectors in order (DOMs change frequently). Stop at first selector that returns ≥ 2 elements.
- For each job card, extract: title (first line usually works), link (first `<a>` inside the card's href), full text as description, any $/₱ numbers as budget.
- Skip cards with <50 chars of text (likely ads / placeholders).
- Skip budgets that look like junk (≤ $4/hr, which is below the grad's floor).
- Return at most `max_jobs` entries.

### Platform-specific search URLs

- **Upwork:** `https://www.upwork.com/nx/search/jobs/?q={keywords}&sort=recency`
- **OnlineJobs.ph:** `https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword={keywords}&jobtype=0&joblocation_city=&jobpay=&jobpaycriteria=0`

**Login handling:** If the page URL after navigation contains `/login` or a login form is detected, print a clear message: `"[Platform] requires login. Please log in manually in the Chrome window — the script will wait 90 seconds."` Then `time.sleep(90)`. Cookies persist in `user_data/` after first run.

---

## 9. The source-of-truth prompt — `prompts/tenxva_outreach.txt`

Write this file exactly:

```
You are the AI Integraterz Outreach Assistant. You help a certified AI Integraterz AI Integrator apply to a job posting on a freelance or job platform. You are NOT a generic cover-letter writer.

Every application you draft MUST satisfy all seven rules below. These are non-negotiable — your output will be audited against them.

RULE 1 — PERSONALIZATION
Line 1 or 2 must reference a SPECIFIC, verifiable detail from the job post (tech stack, company type, stated pain point, timeline, tool they named). Never use generic openers like "I hope this finds you well" or "I came across your post."

RULE 2 — POSITIONING
Position the grad as a certified AI Integrator — NOT a freelancer, NOT an agency. They are an embedded part-time or full-time team member. Use the phrase "embedded team member" or equivalent language at least once.

RULE 3 — CREDENTIALS
Mention, in one sentence: the grad was trained through a US-based certification program that requires mastermind support and a working-system portfolio. Do not name "AI Integraterz" in the body (keep it in the signature). Say something like: "I went through a US-based AI Integrator certification with mastermind support and had to build two working systems to graduate."

RULE 4 — CTA
End with a low-pressure call-to-action: a 15-minute intro call via the calendar link, plus an opt-out: "If I'm not the fit, I may know a teammate from my program who is."

RULE 5 — LENGTH
Under 180 words total (including signature).

RULE 6 — TONE
Professional but human. No emojis. Maximum one exclamation point. No corporate filler ("I hope this email finds you well," "Hope all is well," "I am writing to express my interest"). Contractions are fine.

RULE 7 — SIGNATURE
End with exactly this format on separate lines:
[Grad Name]
Certified AI Integrator | AI Integraterz Program
[Calendar link]
[Portfolio link]

INPUT FORMAT
You will receive:
- JOB TITLE: <text>
- JOB DESCRIPTION: <text>
- GRAD PROFILE: name, calendar link, portfolio link, target niches

OUTPUT FORMAT
Output ONLY the application text (opening + body + signature). Do NOT include the job title, any preamble, any explanation, any "Here is your draft," and do NOT wrap it in code fences.
```

---

## 10. `setup.py` — interactive wizard

1. Check Python version: if `sys.version_info < (3, 10)` → error and exit. If `>= (3, 14)` → warn but continue.
2. If `config.json` and `.env` both exist, ask: `"Config already exists. Overwrite? [y/N]: "`. Default no.
3. Prompt for each field in §5's `config.json`. Show default in brackets, accept empty input to keep default.
4. For niches and keywords: accept comma-separated string, split + strip.
5. Prompt for Gemini API key. Validate with a live call:
   ```python
   genai.configure(api_key=key)
   genai.GenerativeModel("gemini-2.5-flash").generate_content("Say hi in 3 words.")
   ```
   If it raises, print the error and re-prompt once. If it fails again, save anyway and warn.
6. Write `.env` (just `GOOGLE_API_KEY=...`) and `config.json` (pretty-printed JSON).
7. Print next step: `"Setup complete. Run: python run.py"`.

---

## 11. `run.py` — main entry

CLI args (use `argparse`):
- `--platform {upwork,onlinejobs,all}` — default `all`.
- `--smoke-test` — headless mode, 1 job per platform, skip Gemini calls (print stub instead). For verification.
- `--max N` — override `config["drafts_per_run"]`.

Flow:
1. Load `.env`. If no `GOOGLE_API_KEY`, print `"Run: python setup.py first."` and exit 1.
2. Load `config.json`. If missing, same error.
3. `driver = get_driver(headless=args.smoke_test)`.
4. For each selected platform:
   - Print `"→ Scraping {platform}..."`.
   - Call `platform.scrape(driver, config, max_jobs=...)`.
   - For each job returned, call `generate_application(...)` (or stub in smoke test).
   - Append to `all_drafts` list.
5. `driver.quit()`.
6. Write CSVs:
   - Per-platform: `upwork_drafts.csv`, etc.
   - Combined: `daily_drafts.csv`.
   - Columns: `date, platform, title, link, budget, posted_date, application_text`.
   - UTF-8, `csv.QUOTE_ALL` so multi-line text doesn't break Excel.
7. Print Playbook-aligned summary:
   ```
   ✅ Drafted {N} applications.
      Upwork: {a}  OnlineJobs.ph: {b}
   
   📋 Next steps (Playbook Part 6):
      1. Open daily_drafts.csv
      2. Review each — tweak the personalization line if needed
      3. Submit the 5–10 that look like a fit
      4. Log submissions in your AI Integraterz tracking sheet
      5. Post your daily numbers in Skool
   
   📢 Copy-paste for #grad-daily-standup:
      "Day {day} — Drafts ready: {N} ({a} UW / {b} OJP). Plan: submit 5, 50 emails, 15 DMs."
   ```
   (`day` = days since `config["start_date"]`.)

---

## 12. `INSTRUCTIONS_FOR_AI.md`

Write a file Claude Code reads when a grad drops the repo link in. It should instruct Claude to:

1. Check Python version (3.12 ideal, 3.10+ minimum, warn on 3.14+).
2. `python -m venv venv` and activate (PowerShell syntax for Windows, bash for Mac).
3. `pip install -r requirements.txt`.
4. Run `python setup.py` and ask the grad each question conversationally in natural language, then type the answer into the wizard prompt. Specifically:
   - Name, calendar link, portfolio link (point them at their AI Integraterz Operations Agent Loom if they don't have a portfolio yet).
   - Niches — reference the Grad Playbook's starter list if they're stuck.
   - Gemini key — send them to https://aistudio.google.com/apikey, tell them it's free, tell them it starts with `AIza` (newer keys may look different — don't reject unusual formats).
5. Run `python run.py --smoke-test` first — confirm CSV writes.
6. Run `python run.py` — tell them a Chrome window will open. On first run for each platform, they log in manually; the script waits 90 seconds.
7. Open `daily_drafts.csv`, show them how to read one draft, remind them the 7-item audit rubric is built into the prompt.
8. Show the Skool copy-paste line from the summary output.

---

## 13. `README.md`

Short. Three sections:

**What this is** — "The Autonomous Job Agent from your AI Integraterz certification. Pulls recent AI Integrator / automation jobs from Upwork and OnlineJobs.ph, drafts an AI Integraterz-aligned application for each, saves them to CSV for morning review."

**Setup** — "Paste this repo URL into Claude Code and say 'set this up for me.' Claude reads `INSTRUCTIONS_FOR_AI.md` and handles it."

Manual fallback commands for Windows (PowerShell) and Mac (zsh).

**Extend it** — 5 bullets:
- Add Freelancer.com (copy `upwork.py`, change selectors + URL).
- Push `daily_drafts.csv` to a Google Sheet (`gspread`).
- Auto-submit your top pick after you mark it in a "submit?" column.
- Schedule daily runs (Windows Task Scheduler / macOS `cron`).
- Post the Skool summary automatically via Skool's API.

---

## 14. Verification checklist (builder must run before handoff)

1. Delete `venv/`, `user_data/`, `.env`, `config.json` → clean slate.
2. `python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt` — completes with no errors.
3. `python setup.py` — wizard completes, both files written, Gemini key validated.
4. `python run.py --smoke-test` — produces CSV with stubbed applications, no Chrome GUI shown, exit code 0.
5. `python run.py --platform upwork` — Chrome opens, manual login works, ≥2 jobs extracted, ≥2 non-empty applications in CSV.
6. Repeat 5 for `onlinejobs`.
7. Re-run `python run.py --platform upwork` — no login required (cookies persisted).
8. Spot-check 3 applications in `daily_drafts.csv` against the 7-item rubric in §9. All 3 must pass all 7 items.

If any step fails, debug before handing back.

---

## 15. Non-goals (do NOT implement)

- LinkedIn scraper (covered by social DMs channel, not job agent).
- Indeed scraper (dropped from scope; can be added later as an extension).
- Auto-applying / auto-submitting.
- Google Sheets push (leave as README extension).
- Freelancer.com scraper (leave as README extension).
- Telemetry, version checks, explainer mode — mentioned in plan as v2/v3, skip for v1.
- Any form of captcha solving, proxy rotation, or anti-bot workarounds beyond the basic Selenium flags in §6.
