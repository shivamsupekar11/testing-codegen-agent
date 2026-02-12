import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hardcoded path — this tool only edits the TOON test-cases file.
TOON_FILE = os.path.join(PROJECT_PATH, "workspace", "intermediate", "test_cases_template.toon")

def edit_file(
    old_string: str,
    new_string: str,
    replace_all: bool = False,
):
    """
    Edit the TOON test-cases file by replacing string occurrences safely.

    The target file is always:
        workspace/intermediate/test_cases_template.toon

    No file_path argument is needed — the path is hardcoded for safety
    and simplicity so the agent cannot accidentally edit other files.

    Args:
        old_string: The exact text to search for in the file.
        new_string: The replacement text.
        replace_all: If True, replace ALL occurrences of old_string.
                     If False (default) and more than one occurrence exists,
                     an error is returned asking for more context.

    Returns:
        On success:
            {
                "path": "workspace/intermediate/test_cases_template.toon",
                "occurrences": int   # number of replacements made
            }
        On failure:
            {
                "error": str         # human-readable error message
            }
    """
    if not os.path.exists(TOON_FILE) or not os.path.isfile(TOON_FILE):
        return {"error": f"TOON file not found at {TOON_FILE}"}

    try:
        # Prevent symlink attacks (basic check)
        fd = os.open(TOON_FILE, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            content = f.read()

        MAX_FILE_SIZE_MB = 10
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

        stat = os.stat(TOON_FILE)
        if stat.st_size > MAX_FILE_SIZE_BYTES:
            return {"error": "File exceeds maximum allowed size (10MB)"}

        occurrences = content.count(old_string)

        if occurrences == 0:
            return {"error": f"String not found in file: '{old_string}'"}

        if occurrences > 1 and not replace_all:
            return {
                "error": (
                    f"String '{old_string}' appears {occurrences} times in file. "
                    "Use replace_all=True to replace all instances, or provide a more "
                    "specific string with surrounding context."
                )
            }

        new_content = content.replace(old_string, new_string)

        flags = os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW

        fd = os.open(TOON_FILE, flags)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "path": "workspace/intermediate/test_cases_template.toon",
            "occurrences": int(occurrences),
        }

    except (OSError, UnicodeDecodeError, UnicodeEncodeError) as e:
        return {"error": f"Error editing TOON file: {e}"}
