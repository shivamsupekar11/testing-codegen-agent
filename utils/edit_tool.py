import os

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
):
    """
    Edit a file by replacing string occurrences safely.

    Args:
        file_path: Path relative to PROJECT_PATH.
        old_string: Text to search for.
        new_string: Replacement text.
        replace_all: Replace all occurrences if True.

    Returns:
        {
            "path": str,
            "occurrences": int
        }
        OR
        {
            "error": str
        }
    """
    resolved_path = os.path.join(PROJECT_PATH, file_path)

    if not os.path.exists(resolved_path) or not os.path.isfile(resolved_path):
        return {"error": f"File '{file_path}' not found at {resolved_path}"}

    try:
        # Prevent symlink attacks (basic check, less strict than fd)
        fd = os.open(resolved_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            content = f.read()

        MAX_FILE_SIZE_MB = 10
        MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
        
        stat = os.stat(resolved_path)
        if stat.st_size > MAX_FILE_SIZE_BYTES:
            return {"error": "File exceeds maximum allowed size (10MB)"}

        # Logic from perform_string_replacement inline for simplicity or reuse correct function
        occurrences = content.count(old_string)

        if occurrences == 0:
            return f"Error: String not found in file: '{old_string}'"

        if occurrences > 1 and not replace_all:
             return (
                f"Error: String '{old_string}' appears {occurrences} times in file. "
                "Use replace_all=True to replace all instances, or provide a more "
                "specific string with surrounding context."
            )

        new_content = content.replace(old_string, new_string)
        
        flags = os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW

        fd = os.open(resolved_path, flags)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {
            "path": file_path,
            "occurrences": int(occurrences),
        }

    except (OSError, UnicodeDecodeError, UnicodeEncodeError) as e:
        return {"error": f"Error editing file '{file_path}': {e}"}
