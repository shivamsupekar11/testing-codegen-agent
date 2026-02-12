
import os
import sys

# Add project root to path
# __file__ = agent_analyzer/test/test_edit_tool.py
# dirname 1 = agent_analyzer/test
# dirname 2 = agent_analyzer
# dirname 3 = project root (where utils/ is located)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)
os.chdir(PROJECT_ROOT)  # edit_tool uses paths relative to project root

from utils.edit_tool import edit_file, TOON_FILE

# ── The tool is hardcoded to edit: workspace/intermediate/test_cases_template.toon
# ── So we back up the real file, test with it, then restore.

print(f"Target file (hardcoded in edit_tool): {TOON_FILE}\n")

# 1. Back up original content
backup = None
if os.path.exists(TOON_FILE):
    with open(TOON_FILE, "r") as f:
        backup = f.read()

# 2. Write dummy content for testing
print("Writing dummy content to TOON file...")
os.makedirs(os.path.dirname(TOON_FILE), exist_ok=True)
with open(TOON_FILE, "w") as f:
    f.write("module: TestModule\n  tc_id: TC_TEST_001\n  action: verify edit works\n")

with open(TOON_FILE, "r") as f:
    print(f"Initial Content:\n{f.read()}")

# 3. Perform Edit — NOTE: no file_path argument, the tool always edits the TOON file
print("Attempting to replace 'verify edit works' with 'EDIT_SUCCESSFUL'...")
result = edit_file("verify edit works", "EDIT_SUCCESSFUL")
print(f"Result: {result}")

# 4. Verify new content
with open(TOON_FILE, "r") as f:
    content = f.read()
    print(f"\nFinal Content:\n{content}")

if "EDIT_SUCCESSFUL" in content:
    print("\n✅ SUCCESS: The tool successfully edited the .toon file.")
else:
    print("\n❌ FAILURE: The edit did not persist.")

# 5. Restore original content
if backup is not None:
    with open(TOON_FILE, "w") as f:
        f.write(backup)
    print("🔄 Original TOON file restored.")

