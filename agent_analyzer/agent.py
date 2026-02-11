from google.adk.agents.llm_agent import Agent
import sys
import os

# Ensure local xpath_finder is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.xpath_finder import find_xpath, find_multiple_xpath
from utils.read_test_case import tool_read_test_case
from utils.test_case_parser import tool_list_test_cases
from utils.edit_tool import edit_file
from utils.chat_model import get_model_name

root_agent = Agent(
    model=get_model_name(),
    name='agent_analyzer',
    description='Finds XPaths for web elements using fuzzy matching strategies.',
    instruction='You are an expert at finding robust XPath locators. Use find_xpath for single elements and find_multiple_xpath for batch processing. Always prioritize high-confidence results.',
    tools=[find_xpath, find_multiple_xpath, tool_read_test_case, tool_list_test_cases, edit_file],
)
