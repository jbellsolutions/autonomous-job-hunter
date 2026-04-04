import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

load_dotenv()

# --- CONFIGURATION ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Provide your service details here to make the AI pitches high-converting
MY_SERVICE_DETAILS = """
Service: [E.g., Custom AI Automation & Workflow Optimization]
Target Price: [E.g., $2,000 - $5,000 per project]
Unique Value Prop: [E.g., I save businesses 20+ hours a week by automating their lead gen and CRM.]
Experience: [E.g., 5+ years in software engineering, worked with 50+ clients.]
"""

async def run_linkedin_bot():
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in .env file.")
        return

    # Use a persistent context to stay logged in
    browser = Browser(
        config=BrowserConfig(
            headless=False,  # Set to False so you can see it work and log in if needed
            chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", # Adjust for your system if needed
        )
    )

    llm = ChatOpenAI(model="gpt-4o")

    # The Task: Find high-ticket jobs, filter, and draft replies
    task = f"""
    1. Go to 'https://www.linkedin.com/services/marketplace/'
    2. If not logged in, wait for the user to log in manually.
    3. Navigate to 'Project Requests' or the main dashboard where new requests appear.
    4. For each request:
       - **FILTER:** Skip if the budget is explicitly mentioned as low (e.g., <$500) or if the description is only 1 sentence.
       - **ANALYZE:** Identify the core problem the client is facing.
       - **DRAFT:** Create a highly personalized, high-converting pitch.
       - Use these details for the pitch: {MY_SERVICE_DETAILS}.
       - Mention a specific technical or business detail from their request to prove expertise.
       - Ask a "low-friction" question (e.g., "Do you have a specific timeline for this?") to get them to reply.
       - **SAVE:** Write the draft into the 'drafts.txt' file along with the client's name and the link to the request.
       - **DO NOT SEND.** Only type it into the LinkedIn reply box if possible, but definitely save to drafts.txt.
    5. Stop after 10 high-quality drafts are saved.
    """

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    print("🚀 Starting LinkedIn Service Marketplace Agent...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_linkedin_bot())
