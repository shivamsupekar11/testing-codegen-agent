import json
import re
import os

def get_indentation(line):
    return len(line) - len(line.lstrip())

def tool_list_test_cases():
    """
    Parses all TOON files in the workspace/intermediate/archive directory to find the start and end lines of each test case.
    Returns a dictionary in the format:
    {
      "TC_001": { "sl": 1, "el": 10, "file": "filename.toon" },
      ...
    }
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    intermediate_dir = os.path.join(project_root, "workspace", "intermediate", "archive")
    
    # Dynamically find the .toon files
    try:
        files = [f for f in os.listdir(intermediate_dir) if f.endswith('.toon') and not f.startswith('.')]
        if not files:
             return json.dumps({"error": f"No .toon file found in {intermediate_dir}"})
        
        # Sort files by batch number to ensure order
        # Expecting format like TestCases_batch1_TCs1-20_...
        def get_batch_num(filename):
            match = re.search(r'batch(\d+)', filename)
            return int(match.group(1)) if match else float('inf')
            
        files.sort(key=get_batch_num)
        
    except FileNotFoundError:
        return json.dumps({"error": f"Directory not found: {intermediate_dir}"})
    
    results = {}
    
    # Regex to capture tc_id and its value. 
    tc_pattern = re.compile(r'^\s*tc_id:\s*(.+)$')

    for filename in files:
        file_path = os.path.join(intermediate_dir, filename)
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            continue # Skip files that can't be read

        current_tc_id = None
        current_start_line = -1
        current_indent = -1
        
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()
            
            # Skip empty lines
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
                    "el": -1, # Placeholder
                    "file": filename
                }
                
            else:
                # If we are inside a test case
                if current_tc_id:
                    # If indentation drops below the start indentation, the block has ended
                    if indent < current_indent:
                         results[current_tc_id]["el"] = line_num - 1
                         current_tc_id = None
                         current_start_line = -1
                         current_indent = -1
        
        # Close the last test case if file ended
        if current_tc_id and results[current_tc_id]["el"] == -1:
            results[current_tc_id]["el"] = len(lines)

    return json.dumps(results, indent=2)

if __name__ == "__main__":
    print(tool_list_test_cases())
