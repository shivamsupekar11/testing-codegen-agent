from google.adk.agents.llm_agent import Agent
import sys
import os

# Ensure local xpath_finder is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xpath_finder import find_xpath, find_multiple_xpath

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agent_analyzer',
    description='Finds XPaths for web elements using fuzzy matching strategies.',
    instruction='You are an expert at finding robust XPath locators. Use find_xpath for single elements and find_multiple_xpath for batch processing. Always prioritize high-confidence results.',
    tools=[find_xpath, find_multiple_xpath],
)
