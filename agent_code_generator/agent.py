from google.adk.agents import Agent
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from utils.tool_read_test_case import tool_read_test_case
from utils.chat_model import get_model
from utils.file_tools import read_file, list_directory, edit_file

CODE_GENERATOR_PROMPT_PATH = os.path.join(PROJECT_ROOT, "prompts", "code_generator_prompt.md")

# If the prompt file exists, load it. Otherwise, use a default instruction string.
if os.path.exists(CODE_GENERATOR_PROMPT_PATH):
    with open(CODE_GENERATOR_PROMPT_PATH, 'r') as f:
        code_generator_prompt = f.read()
else:
    code_generator_prompt = (
        "You are a Java Code Generator. Read the provided documentation and test cases "
        "to generate valid Java test classes implementing the Logix framework."
    )

root_agent = Agent(
    model=get_model(),
    name='code_generator',
    description='Java Code Generator Agent that reads function documentation and TOON files using tools like read_file and tool_read_test_case, then updates the Java test class using edit_file.',
    instruction=code_generator_prompt,
    tools=[read_file, tool_read_test_case, edit_file, list_directory],
)
