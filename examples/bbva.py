"""
Simple try of the agent.

@dev You need to add OPENAI_API_KEY to your environment variables.
"""

import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig


# Configure browser with physical input and real Chrome instance
config = BrowserConfig(
    use_physical_input=True,
    headless=False,  # To see the physical interactions
    chrome_instance_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # Additional anti-detection measures
    disable_security=True,  # Required for some banking sites
    extra_chromium_args=[
        '--window-size=1280,800',  # Standard window size
        '--disable-blink-features=AutomationControlled',  # Hide automation
    ]
)

# Initialize browser with config
browser = Browser(config=config)

# Initialize LLM
llm = ChatOpenAI(model='gpt-4o')

# Create agent with configured browser
agent = Agent(
    task='Go to https://www.bbva.mx/, log in using this card number: "4152314211632842" and this password: "87RgCFp2r"',
    llm=llm,
    browser=browser,
    max_actions_per_step=4,  # Allow more actions per step for complex interactions
)

async def main():
    try:
        await agent.run(max_steps=20)
        agent.create_history_gif()
    finally:
        # Ensure browser is properly closed
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())