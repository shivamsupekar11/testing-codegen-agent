"""
sync_testng.py
--------------
Reads all @Test-annotated method names from TestWebApp.java
and ensures each one appears as an <include name="..."/> entry
inside the <methods> block of testng.xml.

The project path is read from the .env file (OUTPUT_DIR variable)
located in agent_analyzer/.env (relative to the repo root).

No external dependencies required — runs with plain Python 3.
"""

import re
import os
import sys


# ── Minimal .env parser (no dependencies) ──────────────────────────────
def load_env(env_path: str) -> dict[str, str]:
    """Parse a .env file and return a dict of key=value pairs."""
    env_vars: dict[str, str] = {}
    if not os.path.isfile(env_path):
        return env_vars
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip().strip("'\"")
    return env_vars


# ── Load .env from agent_analyzer/.env ─────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)  # one level up from scripts/
ENV_PATH = os.path.join(REPO_ROOT, "agent_analyzer", ".env")

env = load_env(ENV_PATH)

# ── Read project path from .env ────────────────────────────────────────
OUTPUT_DIR = env.get("OUTPUT_DIR", "").strip()

if not OUTPUT_DIR:
    print("❌ ERROR: OUTPUT_DIR is not set in .env")
    print(f"   Please set it in: {ENV_PATH}")
    sys.exit(1)

if not os.path.isdir(OUTPUT_DIR):
    print(f"❌ ERROR: OUTPUT_DIR does not exist: {OUTPUT_DIR}")
    sys.exit(1)

# ── Derived paths ──────────────────────────────────────────────────────
JAVA_FILE = os.path.join(
    OUTPUT_DIR,
    "src", "test", "java", "com", "logix", "test", "web", "TestWebApp.java",
)
TESTNG_XML = os.path.join(OUTPUT_DIR, "testng.xml")


# ── Step 1: Extract @Test method names from the Java file ─────────────
def extract_test_methods(java_path: str) -> list[str]:
    """Return a list of method names that are annotated with @Test."""
    if not os.path.isfile(java_path):
        print(f"❌ ERROR: Java file not found: {java_path}")
        sys.exit(1)

    with open(java_path, "r") as f:
        content = f.read()

    # Pattern: @Test (possibly with parameters) followed by public void methodName(
    pattern = r"@Test(?:\s*\(.*?\))?\s+public\s+void\s+(\w+)\s*\("
    methods = re.findall(pattern, content, re.DOTALL)
    return methods


# ── Step 2: Update testng.xml ─────────────────────────────────────────
def update_testng_xml(xml_path: str, methods: list[str]) -> None:
    """
    Replace the content between <methods> and </methods> in testng.xml
    with <include name="..."/> entries for every detected test method.
    """
    if not os.path.isfile(xml_path):
        print(f"❌ ERROR: testng.xml not found: {xml_path}")
        sys.exit(1)

    with open(xml_path, "r") as f:
        xml_content = f.read()

    # Build the new <include .../> block
    include_lines = ""
    for i, method in enumerate(methods, start=1):
        include_lines += f'                    <!-- TC{i:02d} -->\n'
        include_lines += f'                    <include name="{method}"/>\n'

    # Replace everything between <methods> ... </methods>
    new_block = f"<methods>\n{include_lines}                </methods>"
    updated_xml = re.sub(
        r"<methods>.*?</methods>",
        new_block,
        xml_content,
        flags=re.DOTALL,
    )

    with open(xml_path, "w") as f:
        f.write(updated_xml)


# ── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"📂 .env file  : {ENV_PATH}")
    print(f"📂 OUTPUT_DIR : {OUTPUT_DIR}")
    print(f"📂 Java file  : {JAVA_FILE}")
    print(f"📂 testng.xml : {TESTNG_XML}")

    # Extract methods
    methods = extract_test_methods(JAVA_FILE)
    print(f"\n✅ Found {len(methods)} @Test methods in TestWebApp.java:")
    for m in methods:
        print(f"   • {m}")

    # Update XML
    update_testng_xml(TESTNG_XML, methods)
    print(f"\n✅ testng.xml has been updated with all {len(methods)} methods.")
