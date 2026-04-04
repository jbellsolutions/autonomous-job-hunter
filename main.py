import argparse
import asyncio
from agents.linkedin_agent import run_linkedin_bot
from agents.upwork_agent import run_upwork_bot
from agents.onlinejobs_agent import run_onlinejobs_bot

async def main():
    parser = argparse.ArgumentParser(description="Autonomous Job Hunter & Pitch Writer")
    parser.add_argument("--platform", choices=["linkedin", "upwork", "onlinejobs"], required=True,
                        help="The platform you want the AI agent to hunt on.")
    
    args = parser.parse_args()

    if args.platform == "linkedin":
        await run_linkedin_bot()
    elif args.platform == "upwork":
        await run_upwork_bot()
    elif args.platform == "onlinejobs":
        await run_onlinejobs_bot()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopping Agent...")
