# 🚀 Autonomous Job Hunter & AI Pitch Writer

This repository is designed to be **Plug and Play** for any AI Assistant (like Claude, Gemini, or ChatGPT Code Interpreters). It automates the process of finding high-ticket job opportunities, analyzing them, and drafting personalized pitches using Browser-Use and LangChain.

## 🤖 Instructions for AI Agents (Zero Setup Required)

If you are an AI reading this repo to set it up for your user, **follow these exact steps sequentially**:

1.  **Check Python Version:** Ensure the system has Python 3.11+. 
    `python3 --version`
2.  **Environment Setup:** Create a virtual environment and activate it.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```
4.  **Configuration (.env):** Check if `.env` exists. If not, copy `.env.example` to `.env` and prompt the user for their `OPENAI_API_KEY`.
    Ensure `BROWSER_CONTEXT_PATH=./user_data` is in the `.env` to keep the user logged in across sessions.
5.  **Service Details Customization:** Before running the bots, read `agents/linkedin_agent.py` and `agents/upwork_agent.py` to ensure the `MY_SERVICE_DETAILS` block accurately reflects the user's high-ticket offering (e.g., Target Price, Service, Value Prop). If empty, ask the user what they are selling.

---

## 🛠️ Usage

To launch the orchestrator, simply run `main.py` with the `--platform` argument:

```bash
python3 main.py --platform [linkedin | upwork | onlinejobs]
```

### Examples
*   **LinkedIn Services:** `python3 main.py --platform linkedin`
*   **Upwork Whale Hunter:** `python3 main.py --platform upwork`
*   **OnlineJobs Enrichment:** `python3 main.py --platform onlinejobs`

## 🛡️ Safety & Anti-Ban Features
*   **Persistent Browser Context:** The agent saves cookies to `user_data/` so you only have to log in once manually. This drastically reduces CAPTCHAs and bot-detection.
*   **Human-in-the-loop (HITL):** By default, the browser runs in `headless=False` mode. The AI types the draft directly into the browser or saves it to `*_drafts.txt` but **waits for the user to click SEND**.

## 📁 Directory Structure
*   `agents/`: Contains the specific scraping and writing logic for each platform.
*   `utils/`: Helper functions for enrichment, logging, and validation.
*   `main.py`: The unified CLI entry point.
