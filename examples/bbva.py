# from langchain_openai import ChatOpenAI
# from browser_use import Agent, BrowserConfig

# config = BrowserConfig(
#     use_physical_input=True,
#     headless=False  # To see the physical interactions
# )

# agent = Agent(
#     task="Navigate to [safe site] and input test credentials",
#     llm=llm,
#     browser=Browser(config=config)
# )



"""
Simple try of the agent.

@dev You need to add OPENAI_API_KEY to your environment variables.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from langchain_openai import ChatOpenAI

from browser_use import Agent, BrowserConfig


config = BrowserConfig(
    use_physical_input=True,
    headless=False  # To see the physical interactions
)

llm = ChatOpenAI(model='gpt-4o')
agent = Agent(
	task='Go to https://www.bbva.mx/, log in using this card number: "4152314211632842" and this password: "87RgCFp2r"',
	llm=llm,
)


async def main():
	await agent.run(max_steps=3)
	agent.create_history_gif()


asyncio.run(main())
