"""
tool_read_test_case.py
======================

Purpose
-------
This module is an **agent tool** that reads and returns test-case content from
a TOON (.toon) file.  It is designed to be called by an AI QA Automation
Analyzer Agent that processes every test case, discovers XPath locators, and
updates the TOON file.

TOON File Format
----------------
A TOON file is a YAML-like, indentation-based format where each test case
block starts with a ``tc_id:`` key.  Blocks are delimited by indentation
levels (a line with *lower* indentation than the ``tc_id:`` line signals the
end of that test case).  A typical block looks like:

    tc_id: TC_002
    title: Login with valid credentials
    steps[5]:
      step_no: 1
      action: Click Let's Start
      element_type: button
      original_hint: text='Let's Start'
      resolved_locators:
        value: ""
        confidence: 0.0
        xpath: ""
        fallbacks[0]:
      ...

Retrieval Modes
---------------
The primary function ``tool_read_test_case()`` supports **two modes**:

1. **By ID** – Pass one or more ``tc_ids`` (list or comma-separated string)
   to retrieve specific test cases by their ID.
   Example: ``tool_read_test_case(tc_ids="TC_001,TC_003")``

2. **By Batch** – Omit ``tc_ids`` and supply a ``batch_index`` (0-based) and
   ``batch_size`` (default 5).  The function returns the Nth batch of test
   cases and prints a header showing batch progress.
   Example: ``tool_read_test_case(batch_index=1, batch_size=5)``

Auto-Advancing State (CLI only)
-------------------------------
When run from the command line *without* arguments, the script uses a
persistent state file (``workspace/intermediate/.batch_state``) to
automatically advance through batches on each successive invocation.
This means an agent can simply re-invoke the script repeatedly to walk
through all batches without manually tracking the index.

CLI Usage
---------
    # Auto-advance through batches (uses state file)
    python utils/tool_read_test_case.py

    # Read a specific batch by index
    python utils/tool_read_test_case.py 2

    # Read specific test cases by ID
    python utils/tool_read_test_case.py TC_001,TC_003

    # Reset the batch counter
    python utils/tool_read_test_case.py --reset

File Layout
-----------
- ``TOON_FILE``  – Relative path to the TOON file being read.
- ``STATE_FILE`` – Relative path to the batch-state persistence file.

Dependencies
------------
None beyond the Python standard library (``sys``, ``os``, ``re``).
"""

import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOON_FILE = os.path.join(PROJECT_ROOT, "workspace", "intermediate", "test_cases_template.toon")

def get_indentation(line):
    """Return the number of leading whitespace characters in *line*.

    This is used internally to detect indentation-based block boundaries
    in the TOON file.  A decrease in indentation relative to the ``tc_id:``
    line signals the end of that test-case block.

    Args:
        line (str): A single line of text (may include a trailing newline).

    Returns:
        int: Count of leading whitespace characters (spaces/tabs).

    Example:
        >>> get_indentation('    tc_id: TC_001')
        4
        >>> get_indentation('module: Login')
        0
    """
    return len(line) - len(line.lstrip())

def parse_toon_structure(file_path):
    """Parse the TOON file and map every test-case ID to its line range.

    Scans the file line-by-line looking for ``tc_id:`` entries.  For each
    test case it records:

    - **id**     – The test-case identifier (e.g. ``TC_001``).
    - **sl**     – Start line number (1-based, inclusive).
    - **el**     – End line number (1-based, inclusive).
    - **indent** – Indentation level of the ``tc_id:`` line (used
                   internally to detect block boundaries).

    Block boundaries are determined by indentation: when a non-empty line
    with *lower* indentation than the ``tc_id:`` line is encountered, the
    current test-case block is closed.

    Args:
        file_path (str): Relative or absolute path to the ``.toon`` file.

    Returns:
        tuple:
            - **tc_mapping** (list[dict]): Ordered list of dicts, each with
              keys ``id`` (str), ``sl`` (int), ``el`` (int), ``indent`` (int).
              Returns an empty list if the file is not found or contains
              no ``tc_id`` entries.
            - **lines** (list[str]): Raw lines of the file (each line
              retains its trailing newline).  Useful for extracting the
              actual content of a test case via slicing.

    Raises:
        Nothing – ``FileNotFoundError`` is caught internally and results
        in an empty list being returned.

    Example:
        >>> mapping, lines = parse_toon_structure('workspace/intermediate/test_cases_template.toon')
        >>> mapping[0]
        {'id': 'TC_001', 'sl': 3, 'el': 25, 'indent': 2}
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return [], []

    tc_mapping = []
    
    # Regex to capture tc_id and its value. 
    tc_pattern = re.compile(r'^\s*tc_id:\s*(.+)$')
    
    current_tc = None
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        if not stripped:
            continue
            
        indent = get_indentation(line)
        match = tc_pattern.match(line)
        
        if match:
            # Close previous if exists
            if current_tc:
                current_tc['el'] = line_num - 1
                tc_mapping.append(current_tc)
            
            # Start new
            current_tc = {
                'id': match.group(1).strip(),
                'sl': line_num,
                'el': -1,
                'indent': indent
            }
        
        elif current_tc:
            # Check for end of block by indentation
            # If we see a line with equal or lower indentation than the start of the TC block,
            # it means the block has ended (unless it's empty, checked above)
            if indent < current_tc['indent']:
                 current_tc['el'] = line_num - 1
                 tc_mapping.append(current_tc)
                 current_tc = None

    # Handle last one
    if current_tc:
        current_tc['el'] = len(lines)
        tc_mapping.append(current_tc)
        
    return tc_mapping, lines

def tool_read_test_case(tc_ids=None, batch_index=0, batch_size=5):
    """Retrieve one or more test cases from the TOON file as raw text.

    This is the **primary entry-point** for an AI agent that needs to read
    test-case definitions before processing them (e.g. finding XPaths and
    editing the file).

    Two mutually-exclusive retrieval modes are supported:

    **Mode 1 – By ID (``tc_ids`` provided)**
        Supply specific test-case IDs and only those test cases are
        returned.  Useful when the agent already knows which cases it
        needs to re-read or retry.

        >>> tool_read_test_case(tc_ids='TC_001,TC_003')
        >>> tool_read_test_case(tc_ids=['TC_002'])

    **Mode 2 – By Batch (``tc_ids`` is ``None``)**
        Returns a paginated slice of all test cases.  The output includes
        a header comment showing batch progress and a hint for the next
        ``batch_index`` value, e.g.::

            # Batch 1 of 3 (Test Cases 1-5 of 12)
            # Contains 5 test cases. Use batch_index=1 for next batch.

        >>> tool_read_test_case(batch_index=0, batch_size=5)  # first 5
        >>> tool_read_test_case(batch_index=1, batch_size=5)  # next 5

    Args:
        tc_ids (list[str] | str | None):
            • ``None`` (default) – use batch mode.
            • ``str``  – comma-separated IDs, e.g. ``'TC_001,TC_003'``.
            • ``list``  – list of ID strings, e.g. ``['TC_001', 'TC_003']``.
        batch_index (int):
            Zero-based batch number.  Only used when ``tc_ids is None``.
            Defaults to ``0`` (the first batch).
        batch_size (int):
            Number of test cases per batch.  Defaults to ``5``.

    Returns:
        str: The raw TOON-formatted content of the selected test cases,
        preceded by an optional batch-progress header.  The returned text
        is the **exact** content that appears in the file, preserving
        indentation and whitespace.  This is important because downstream
        tools (e.g. ``edit_file``) require exact string matching.

        If no test cases match, returns:
        ``'No test cases found matching criteria.'``

        If the TOON file cannot be parsed, returns:
        ``'Error: Could not parse <filepath>'``

    Side Effects:
        None – this function is read-only.  It does **not** modify the
        TOON file or the batch-state file.

    Notes for the Agent:
        • Always call this tool *before* ``edit_file`` so you have the
          exact ``old_string`` content for replacement.
        • The output preserves original whitespace/indentation exactly.
          Copy substrings verbatim when building ``edit_file`` calls.
        • When using batch mode, the header comment tells you the next
          ``batch_index`` to use.  Keep calling until you see
          ``'# End of Test Cases.'``.
    """
    mapping, lines = parse_toon_structure(TOON_FILE)
    
    if not mapping:
        return f"Error: Could not parse {TOON_FILE}"

    selected_tcs = []

    # Mode 1: Specific IDs
    if tc_ids:
        if isinstance(tc_ids, str):
            target_ids = [t.strip() for t in tc_ids.split(',')]
        else:
            target_ids = tc_ids
            
        for m in mapping:
            if m['id'] in target_ids:
                selected_tcs.append(m)
    
    # Mode 2: Batching
    else:
        try:
            batch_index = int(batch_index)
        except ValueError:
            batch_index = 0
            
        start_idx = batch_index * batch_size
        end_idx = start_idx + batch_size
        selected_tcs = mapping[start_idx:end_idx]

    if not selected_tcs:
        return "No test cases found matching criteria."

    param_info = ""
    if not tc_ids:
        total_tcs = len(mapping)
        total_batches = (total_tcs + batch_size - 1) // batch_size
        current_batch = batch_index + 1
        
        param_info = f"# Batch {current_batch} of {total_batches} (Test Cases {start_idx + 1}-{min(end_idx, total_tcs)} of {total_tcs})\n"
        if current_batch < total_batches:
             param_info += f"# Contains {len(selected_tcs)} test cases. Use batch_index={current_batch} for next batch.\n"
        else:
             param_info += "# End of Test Cases.\n"

    output = [param_info]
    for tc in selected_tcs:
        # Extract lines. converting 1-based line nums to 0-based list indices
        chunk = "".join(lines[tc['sl']-1 : tc['el']])
        output.append(chunk)

    return "\n".join(output)

STATE_FILE = os.path.join(PROJECT_ROOT, "workspace", "intermediate", ".batch_state")

def load_state():
    """Load the current batch index from the persistent state file.

    The state file (``workspace/intermediate/.batch_state``) stores a
    single integer representing the next ``batch_index`` to process.
    This enables the CLI's auto-advance behaviour: each invocation reads
    the next batch without the caller needing to track the index.

    Returns:
        int: The stored batch index.  Returns ``0`` if the state file
        does not exist or contains an invalid value.
    """
    try:
        with open(STATE_FILE, 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_state(index):
    """Persist the given batch index to the state file.

    Writes *index* as a plain-text integer to
    ``workspace/intermediate/.batch_state``.  If writing fails (e.g.
    permission error), a warning is printed to ``stderr`` but no
    exception is raised, so execution can continue.

    Args:
        index (int): The batch index to save (0-based).

    Side Effects:
        Creates or overwrites the state file.
    """
    try:
        with open(STATE_FILE, 'w') as f:
            f.write(str(index))
    except Exception as e:
        sys.stderr.write(f"Warning: Could not save state: {e}\n")

if __name__ == "__main__":
    # If arguments are provided, use them (manual override)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.isdigit():
             print(tool_read_test_case(batch_index=int(arg)))
        elif arg.lower() in ('--reset', '-r'):
             save_state(0)
             print("Batch state reset to 0.")
        else:
             print(tool_read_test_case(tc_ids=arg))
    else:
        # Automatic mode: Use state file
        current_idx = load_state()
        
        # Check total batches to see if we should reset or proceed
        mapping, _ = parse_toon_structure(TOON_FILE)
        batch_size = 5
        total_batches = (len(mapping) + batch_size - 1) // batch_size
        
        if current_idx >= total_batches and total_batches > 0:
            # We reached the end previously
            print(f"# All {len(mapping)} test cases have been processed. Resetting to beginning.")
            save_state(0)
            current_idx = 0
            
        output = tool_read_test_case(batch_index=current_idx, batch_size=batch_size)
        print(output)
        
        # Increment for next time
        if "End of Test Cases" not in output and "No test cases found" not in output:
             save_state(current_idx + 1)
        else:
             # We just finished or are at the end
             print("# Cycle complete. Resetting state for next run.")
             save_state(0)
