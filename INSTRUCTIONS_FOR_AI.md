# 🤖 ATTENTION: AI AGENT / ASSISTANT

If you have been given this folder, your goal is to set up and run the **Autonomous Job Hunter** for the user. 

### 🛠️ Step 1: Initialize Environment
Run these commands to prepare the environment:
```bash
bash setup.sh
```

### 🔑 Step 2: Configure API Key
Ask the user for their **OpenAI API Key** if it's not already in the `.env` file.
Update the `.env` file:
```bash
echo "OPENAI_API_KEY=sk-..." > .env
```

### 🎯 Step 3: Define the Pitch
Ask the user: "What services are you selling and what is your target price point?"
Update the `MY_SERVICE_DETAILS` variable in:
- `agents/linkedin_agent.py`
- `agents/upwork_agent.py`

### 🚀 Step 4: Launch the Bot
Once configured, ask the user which platform they want to target and run:
```bash
python3 main.py --platform [linkedin | upwork | onlinejobs]
```

---
**Note to AI:** This tool uses `browser-use`. It will open a real browser window. Instruct the user that they must log in manually during the first run, and the AI will take over after that.
