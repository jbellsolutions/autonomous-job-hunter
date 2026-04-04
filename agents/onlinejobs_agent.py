import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

load_dotenv()

# The logic: Scan OnlineJobs.ph -> Extract Employer -> Search LinkedIn/Google -> Decide if "Whale" -> Draft Pitch
async def run_onlinejobs_bot():
    browser = Browser(config=BrowserConfig(headless=False))
    llm = ChatOpenAI(model="gpt-4o")

    # The Task: Find high-quality employers and enrich their data
    task = """
    1. Go to 'https://www.onlinejobs.ph/jobsearch'
    2. Search for: 'Project Manager' or 'Technical Architect' or 'Automation Expert'.
    3. For each high-salary request (e.g. > $1,500/mo or mentioning 'Commission'):
       - **ENRICH:** Search for the employer's company name on Google and LinkedIn.
       - **VALUATE:** If the company is a VC-backed startup or established US/EU firm, proceed.
       - **DRAFT:** Create a pitch that mentions their recent company news (if found) or their specific industry challenges.
       - **SAVE:** Write to 'onlinejobs_drafts.txt'.
    4. Stop after 5 enriched leads.
    """

    agent = Agent(task=task, llm=llm, browser=browser)
    print("🚀 Starting OnlineJobs Enrichment Agent...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(run_onlinejobs_bot())
