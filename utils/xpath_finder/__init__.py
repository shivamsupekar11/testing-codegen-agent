"""
XPath Finder Tool for Google ADK Agents

Usage:
    from xpath_finder import find_xpath, find_multiple_xpath
    
    # In your ADK agent:
    agent = Agent(
        model='gemini-2.5-flash', 
        tools=[find_xpath, find_multiple_xpath]
    )
"""

from .tool import find_xpath, find_multiple_xpath


__all__ = ["find_xpath", "find_multiple_xpath"]

