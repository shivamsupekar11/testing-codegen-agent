"""
file_tools.py
=============

Standalone filesystem utility tools for an AI agent.

Provides three tools that operate relative to the project root:

- **read_file(file_path)**        – Read the contents of a file.
- **list_directory(path)**        – List files and subdirectories in a directory.
- **edit_file(file_path, ...)**   – Edit a file by replacing exact string occurrences.

All paths are resolved relative to ``PROJECT_PATH`` (the project root).
Path-traversal attempts (e.g. ``../../etc/passwd``) are blocked.

Note
----
This module is intentionally **dependency-free** beyond the Python standard
library so it can be used with any agent framework (Google ADK, LangChain, etc.).
"""

import os
from pathlib import Path

PROJECT_PATH = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "workspace" / "output" / "testing-templates"

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _resolve_safe(relative_path: str) -> Path | None:
    """Resolve *relative_path* under PROJECT_PATH and verify it doesn't escape.

    Returns the resolved ``Path`` on success, or ``None`` if the path
    would escape the project root (path-traversal protection).
    """
    resolved = (PROJECT_PATH / relative_path).resolve()
    if not str(resolved).startswith(str(PROJECT_PATH.resolve())):
        return None
    return resolved


# ──────────────────────────────────────────────
# Tool 1 – read_file
# ──────────────────────────────────────────────

def read_file(file_path: str) -> dict:
    """Read the contents of a file.

    The file is located relative to the project root directory.

    Args:
        file_path (str): Relative path to the file from the project root.
            Example: ``"workspace/intermediate/test_cases_template.toon"``

    Returns:
        dict: On success::

            {
                "path": "workspace/intermediate/test_cases_template.toon",
                "content": "<file contents as string>"
            }

        On failure::

            {
                "error": "<human-readable error message>"
            }
    """
    resolved = _resolve_safe(file_path)
    if resolved is None:
        return {"error": f"Access denied: path '{file_path}' is outside the project."}

    if not resolved.exists():
        return {"error": f"File not found: '{file_path}'"}

    if not resolved.is_file():
        return {"error": f"Not a file: '{file_path}' (maybe a directory?)"}

    try:
        size = resolved.stat().st_size
        if size > MAX_FILE_SIZE_BYTES:
            return {"error": f"File '{file_path}' exceeds maximum size ({MAX_FILE_SIZE_MB}MB)."}

        fd = os.open(resolved, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            content = f.read()

        return {"path": file_path, "content": content}

    except UnicodeDecodeError:
        return {"error": f"Cannot read '{file_path}': file is not valid UTF-8 text."}
    except OSError as e:
        return {"error": f"Error reading '{file_path}': {e}"}


# ──────────────────────────────────────────────
# Tool 2 – list_directory
# ──────────────────────────────────────────────

def list_directory(path: str = ".") -> dict:
    """List the contents of a directory.

    The directory is located relative to the project root.  Returns a
    structured listing with file sizes and subdirectory indicators.

    Args:
        path (str): Relative path to the directory from the project root.
            Defaults to ``"."`` (the project root itself).

    Returns:
        dict: On success::

            {
                "path": "workspace",
                "entries": [
                    {"name": "input",    "type": "directory"},
                    {"name": "data.csv", "type": "file", "size_bytes": 1234},
                    ...
                ]
            }

        On failure::

            {
                "error": "<human-readable error message>"
            }
    """
    resolved = _resolve_safe(path)
    if resolved is None:
        return {"error": f"Access denied: path '{path}' is outside the project."}

    if not resolved.exists():
        return {"error": f"Directory not found: '{path}'"}

    if not resolved.is_dir():
        return {"error": f"Not a directory: '{path}' (maybe a file?)"}

    try:
        entries = []
        for item in sorted(resolved.iterdir()):
            # Skip hidden files/dirs and __pycache__
            if item.name.startswith(".") or item.name == "__pycache__":
                continue

            if item.is_dir():
                entries.append({"name": item.name, "type": "directory"})
            elif item.is_file():
                try:
                    size = item.stat().st_size
                except OSError:
                    size = None
                entry = {"name": item.name, "type": "file"}
                if size is not None:
                    entry["size_bytes"] = size
                entries.append(entry)

        return {"path": path, "entries": entries}

    except PermissionError:
        return {"error": f"Permission denied: cannot list '{path}'."}
    except OSError as e:
        return {"error": f"Error listing '{path}': {e}"}


# ──────────────────────────────────────────────
# Tool 3 – edit_file
# ──────────────────────────────────────────────

def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> dict:
    """Edit a file by replacing exact string occurrences.

    Searches for ``old_string`` in the file and replaces it with
    ``new_string``.  By default only a single occurrence is allowed;
    if more than one is found, an error is returned unless
    ``replace_all=True``.

    Args:
        file_path (str): Relative path to the file from the project root.
            Example: ``"workspace/intermediate/test_cases_template.toon"``
        old_string (str): The exact text to search for in the file.
            Must match the file content **exactly** (whitespace-sensitive).
        new_string (str): The replacement text.
        replace_all (bool): If ``True``, replace **all** occurrences.
            If ``False`` (default) and more than one occurrence exists,
            an error is returned asking for more context.

    Returns:
        dict: On success::

            {
                "path": "workspace/intermediate/test_cases_template.toon",
                "occurrences": 1
            }

        On failure::

            {
                "error": "<human-readable error message>"
            }
    """
    resolved = _resolve_safe(file_path)
    if resolved is None:
        return {"error": f"Access denied: path '{file_path}' is outside the project."}

    if not resolved.exists() or not resolved.is_file():
        return {"error": f"File not found: '{file_path}'"}

    try:
        # Check file size
        size = resolved.stat().st_size
        if size > MAX_FILE_SIZE_BYTES:
            return {"error": f"File '{file_path}' exceeds maximum size ({MAX_FILE_SIZE_MB}MB)."}

        # Read (with symlink protection)
        fd = os.open(resolved, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            content = f.read()

        # Count occurrences
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

        # Perform replacement
        new_content = content.replace(old_string, new_string)

        # Write back (with symlink protection)
        flags = os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        fd = os.open(resolved, flags)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)

        return {"path": file_path, "occurrences": int(occurrences)}

    except UnicodeDecodeError:
        return {"error": f"Cannot edit '{file_path}': file is not valid UTF-8 text."}
    except (OSError, UnicodeEncodeError) as e:
        return {"error": f"Error editing file '{file_path}': {e}"}
