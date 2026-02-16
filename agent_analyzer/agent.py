from google.adk.agents import Agent
import sys
import os



# Ensure local xpath_finder is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.xpath_finder import find_xpath, find_multiple_xpath
from utils.tool_read_test_case import tool_read_test_case
from utils.tool_list_test_cases import tool_list_test_cases
from utils.edit_tool import edit_file
from utils.chat_model import get_model

# Load the system prompt from the markdown file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_PROMPT_PATH = os.path.join(PROJECT_ROOT, "prompts", "system_prompt.md")

with open(SYSTEM_PROMPT_PATH, 'r') as f:
    system_prompt = f.read()

root_agent = Agent(
    model=get_model(),
    name='agent_analyzer',
    description='Expert QA Automation Analyzer Agent that systematically processes every test case in a TOON file, discovers the most accurate XPath locators for each UI element, and updates the TOON file with those locators.',
    instruction=system_prompt,
    tools=[find_xpath, find_multiple_xpath, tool_read_test_case, tool_list_test_cases, edit_file],
)


