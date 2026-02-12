import json
import re
import os

def get_indentation(line):
    return len(line) - len(line.lstrip())

def tool_list_test_cases():
    """
    Parses the TOON file to find the start and end lines of each test case.
    Returns a dictionary in the format:
    {
      "TC_001": { "sl": 1, "el": 10 },
      ...
    }
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "workspace", "intermediate", "test_cases_template.toon")
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return json.dumps({"error": f"File not found: {file_path}"})

    results = {}
    
    # helper to find test cases
    # We look for lines like: "  tc_id: TC_XXX"
    # We assume 'tc_id' is the start of the test case block.
    
    current_tc_id = None
    current_start_line = -1
    current_indent = -1
    
    # Regex to capture tc_id and its value. 
    # Matches: "  tc_id: TC_001 " -> group(1) = "TC_001"
    tc_pattern = re.compile(r'^\s*tc_id:\s*(.+)$')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # Skip empty lines, but they are part of the previous block strictly speaking
        if not stripped:
            continue
            
        indent = get_indentation(line)
        match = tc_pattern.match(line)
        
        if match:
            # We found a new test case start
            new_tc_id = match.group(1).strip()
            
            # If we were processing a test case, close it
            if current_tc_id:
                results[current_tc_id]["el"] = line_num - 1
            
            # Start new test case
            current_tc_id = new_tc_id
            current_start_line = line_num
            current_indent = indent
            
            results[current_tc_id] = {
                "sl": current_start_line,
                "el": -1 # Placeholder
            }
            
        else:
            # If we are inside a test case
            if current_tc_id:
                # If indentation drops below the start indentation, the block has ended
                if indent < current_indent:
                     # This check works because TOON/YAML hierarchy implies children are indented.
                     # Siblings are at same indent. Parents are at lower indent.
                     # If we see a line with lower indent (e.g. 'module: ...'), the previous TC block is done.
                     results[current_tc_id]["el"] = line_num - 1
                     current_tc_id = None
                     current_start_line = -1
                     current_indent = -1
                
                # If indentation is same, it's just another property of the current TC 
                # OR it's a new TC (handled by the 'if match' block above).
                # So we just continue.

    # Close the last test case if file ended
    if current_tc_id and results[current_tc_id]["el"] == -1:
        results[current_tc_id]["el"] = len(lines)

    return json.dumps(results, indent=2)

if __name__ == "__main__":
    print(tool_list_test_cases())
