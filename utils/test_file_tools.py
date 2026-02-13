"""
Quick test for utils/file_tools.py
Run:  python utils/test_file_tools.py
"""

import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_tools import read_file, list_directory, edit_file, PROJECT_PATH

SEPARATOR = "=" * 60

# We'll use a temp file under workspace/ for testing
TEST_FILE_REL = "workspace/test_file_tools_temp.txt"
TEST_FILE_ABS = os.path.join(PROJECT_PATH, TEST_FILE_REL)


def setup():
    """Create a temporary test file."""
    os.makedirs(os.path.dirname(TEST_FILE_ABS), exist_ok=True)
    with open(TEST_FILE_ABS, "w") as f:
        f.write("Hello World\nThis is line two.\nHello World again.\n")
    print(f"✅ Created test file: {TEST_FILE_REL}\n")


def cleanup():
    """Remove the temporary test file."""
    if os.path.exists(TEST_FILE_ABS):
        os.remove(TEST_FILE_ABS)
        print(f"\n🧹 Cleaned up: {TEST_FILE_REL}")


def test_list_directory():
    print(SEPARATOR)
    print("TEST: list_directory")
    print(SEPARATOR)

    # List the project root
    result = list_directory(".")
    print(f"\n📂 list_directory('.') =>")
    if "error" in result:
        print(f"   ❌ {result['error']}")
    else:
        for entry in result["entries"]:
            icon = "📁" if entry["type"] == "directory" else "📄"
            size = f" ({entry.get('size_bytes', '?')} bytes)" if entry["type"] == "file" else ""
            print(f"   {icon} {entry['name']}{size}")

    # List workspace
    result2 = list_directory("workspace")
    print(f"\n📂 list_directory('workspace') =>")
    if "error" in result2:
        print(f"   ❌ {result2['error']}")
    else:
        for entry in result2["entries"]:
            icon = "📁" if entry["type"] == "directory" else "📄"
            size = f" ({entry.get('size_bytes', '?')} bytes)" if entry["type"] == "file" else ""
            print(f"   {icon} {entry['name']}{size}")

    # Error case: non-existent directory
    result3 = list_directory("does_not_exist")
    print(f"\n📂 list_directory('does_not_exist') =>")
    print(f"   {'❌' if 'error' in result3 else '✅'} {result3}")

    # Error case: path traversal
    result4 = list_directory("../../")
    print(f"\n📂 list_directory('../../') =>")
    print(f"   {'❌ Blocked (expected)' if 'error' in result4 else '⚠️  NOT blocked!'} {result4}")


def test_read_file():
    print(f"\n{SEPARATOR}")
    print("TEST: read_file")
    print(SEPARATOR)

    # Read the test file
    result = read_file(TEST_FILE_REL)
    print(f"\n📖 read_file('{TEST_FILE_REL}') =>")
    if "error" in result:
        print(f"   ❌ {result['error']}")
    else:
        print(f"   ✅ path: {result['path']}")
        print(f"   Content:\n   ---")
        for line in result["content"].splitlines():
            print(f"   | {line}")
        print("   ---")

    # Read .env file
    result2 = read_file(".env")
    print(f"\n📖 read_file('.env') =>")
    if "error" in result2:
        print(f"   ❌ {result2['error']}")
    else:
        print(f"   ✅ path: {result2['path']} (content has {len(result2['content'])} chars)")

    # Error case: non-existent file
    result3 = read_file("no_such_file.txt")
    print(f"\n📖 read_file('no_such_file.txt') =>")
    print(f"   {'❌ Expected error' if 'error' in result3 else '⚠️'}: {result3}")


def test_edit_file():
    print(f"\n{SEPARATOR}")
    print("TEST: edit_file")
    print(SEPARATOR)

    # --- Test 1: Single replacement (should fail — "Hello World" appears twice)
    print("\n🔧 Test 1: edit_file — single match expected but 2 found")
    result = edit_file(TEST_FILE_REL, "Hello World", "Hi There")
    print(f"   {'❌ Expected error' if 'error' in result else '⚠️'}: {result}")

    # --- Test 2: Replace all occurrences
    print("\n🔧 Test 2: edit_file — replace_all=True")
    result2 = edit_file(TEST_FILE_REL, "Hello World", "Hi There", replace_all=True)
    print(f"   {'✅' if 'occurrences' in result2 else '❌'}: {result2}")

    # Verify the edit worked
    verify = read_file(TEST_FILE_REL)
    if "content" in verify:
        print(f"   File now reads:")
        for line in verify["content"].splitlines():
            print(f"   | {line}")

    # --- Test 3: Replace a unique string
    print("\n🔧 Test 3: edit_file — unique string replacement")
    result3 = edit_file(TEST_FILE_REL, "line two", "line TWO")
    print(f"   {'✅' if 'occurrences' in result3 else '❌'}: {result3}")

    # --- Test 4: String not found
    print("\n🔧 Test 4: edit_file — string not found")
    result4 = edit_file(TEST_FILE_REL, "does not exist in file", "replacement")
    print(f"   {'❌ Expected error' if 'error' in result4 else '⚠️'}: {result4}")

    # --- Test 5: File not found
    print("\n🔧 Test 5: edit_file — file not found")
    result5 = edit_file("nonexistent.txt", "old", "new")
    print(f"   {'❌ Expected error' if 'error' in result5 else '⚠️'}: {result5}")


if __name__ == "__main__":
    print(f"Project Root: {PROJECT_PATH}\n")
    setup()
    try:
        test_list_directory()
        test_read_file()
        test_edit_file()
    finally:
        cleanup()
    print(f"\n{'=' * 60}")
    print("🎉 All tests completed!")
