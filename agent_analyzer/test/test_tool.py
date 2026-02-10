"""
Simple test script for the XPath Finder Tool.

Run from the project root:
    python -m agent_analyzer.test.test_tool
"""

import asyncio
import json
import sys
import os

# Add project root to path so we can import the tool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agent_analyzer.xpath_finder.tool import find_xpath, find_multiple_xpath


# ── Configuration ────────────────────────────────────────────────────
TEST_URL = "https://www.google.com"  # Change this to any URL you want to test

# Single element hints to test with find_xpath
SINGLE_HINTS = [
    {"hint": "Search", "element_type": "*", "top_n": 5},
    {"hint": "Gmail", "element_type": "a", "top_n": 3},
    {"hint": "Google Search", "element_type": "input", "top_n": 3},
]

# Multiple hints to test with find_multiple_xpath
MULTI_HINTS = ["Search", "Gmail", "I'm Feeling Lucky"]
# ─────────────────────────────────────────────────────────────────────


def print_separator(title: str):
    """Print a formatted section separator."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_results(results):
    """Pretty-print a list of candidate results."""
    if not results:
        print("  ⚠️  No results found.")
        return
    for item in results:
        print(f"\n  Rank {item.get('rank', '?')}:")
        print(f"    XPath      : {item.get('xpath', 'N/A')}")
        print(f"    Confidence : {item.get('confidence', 'N/A')}")
        print(f"    Tag        : {item.get('tag', 'N/A')}")
        print(f"    Text       : {item.get('text', 'N/A')}")
        print(f"    Strategy   : {item.get('strategy', 'N/A')}")
        print(f"    CSS        : {item.get('css', 'N/A')}")
        print(f"    Match Count: {item.get('match_count', 'N/A')}")
        attrs = item.get("attributes", {})
        if attrs:
            print(f"    Attributes : {json.dumps(attrs, indent=2)}")


async def test_find_xpath():
    """Test the find_xpath function with single element hints."""
    print_separator("Testing find_xpath (single element)")

    for test in SINGLE_HINTS:
        hint = test["hint"]
        element_type = test["element_type"]
        top_n = test["top_n"]

        print(f"\n🔍 Searching for: '{hint}' (type={element_type}, top_n={top_n})")
        print("-" * 50)

        try:
            results = await find_xpath(
                url=TEST_URL,
                hint=hint,
                element_type=element_type,
                top_n=top_n,
            )
            print_results(results)
        except Exception as e:
            print(f"  ❌ Error: {e}")


async def test_find_multiple_xpath():
    """Test the find_multiple_xpath function with multiple hints."""
    print_separator("Testing find_multiple_xpath (batch)")

    print(f"\n🔍 Searching for multiple hints: {MULTI_HINTS}")
    print("-" * 50)

    try:
        results = await find_multiple_xpath(
            url=TEST_URL,
            hints=MULTI_HINTS,
            top_n=3,
        )

        for hint, candidates in results.items():
            print(f"\n📌 Hint: '{hint}'")
            print_results(candidates)

    except Exception as e:
        print(f"  ❌ Error: {e}")


async def main():
    """Run all tests."""
    print("🚀 XPath Finder Tool — Simple Test Script")
    print(f"   Target URL: {TEST_URL}")

    await test_find_xpath()
    await test_find_multiple_xpath()

    print_separator("Done!")
    print("  ✅ All tests completed.\n")


if __name__ == "__main__":
    asyncio.run(main())
