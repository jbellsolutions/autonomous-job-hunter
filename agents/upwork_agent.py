import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

load_dotenv()

MY_SERVICE_DETAILS = """
Service: [Update this: e.g. Custom AI Agents & Enterprise Automations]
Target Price: [Update this: e.g. $5,000 - $15,000]
Value Prop: [Update this: e.g. We automate complex workflows that save $100k+ in OpEx.]
"""

async def run_upwork_bot():
    browser = Browser(config=BrowserConfig(headless=False))
    llm = ChatOpenAI(model="gpt-4o")

    # The Task: Find whale clients and draft high-value pitches
    task = f"""
    1. Go to 'https://www.upwork.com/nx/find-work/'
    2. Search for: 'Custom AI Automation' or 'Enterprise Solution Architecture'.
    3. FILTER:
       - Client must be 'Payment Verified'.
       - Client should have spent > $5k on the platform.
       - Job must be 'Fixed Price' (aiming for $2k-$10k).
    4. For each qualifying job:
       - ANALYZE the description for 'Pain Points'.
       - DRAFT a reply that specifically addresses those pain points using: {MY_SERVICE_DETAILS}.
       - Include a 'Relevant Case Study' mention (make up a placeholder if needed).
       - SAVE the draft to 'upwork_drafts.txt'.
    5. Stop after 5 whale leads are drafted.
    """

    agent = Agent(task=task, llm=llm, browser=browser)
    print("🚀 Starting Upwork Whale Hunter...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_upwork_bot())
