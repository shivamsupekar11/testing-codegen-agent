import json
import re

def get_line_number(content, index):
    return content.count('\n', 0, index) + 1

def tool_list_test_cases():
    """
    Parses the JSON file to find the start and end lines of each test case.
    Returns a dictionary in the format:
    {
      "TC_001": { "sl": 1, "el": 10 },
      ...
    }
    """
    file_path = "workspace/intermediate/test_cases_template_output.json"
    
    with open(file_path, 'r') as f:
        content = f.read()

    results = {}
    
    # Find all occurrences of "tc_id": "VALUE"
    matches = list(re.finditer(r'"tc_id"\s*:\s*"(.*?)"', content))
    
    for match in matches:
        tc_id = match.group(1)
        start_search_idx = match.start()
        
        # Find opening brace backwards
        open_brace_idx = -1
        depth = 0
        for i in range(start_search_idx, -1, -1):
            char = content[i]
            if char == '}':
                depth += 1
            elif char == '{':
                if depth == 0:
                    open_brace_idx = i
                    break
                depth -= 1
        
        # Find closing brace forwards
        close_brace_idx = -1
        depth = 0
        for i in range(match.end(), len(content)):
            char = content[i]
            if char == '{':
                depth += 1
            elif char == '}':
                if depth == 0:
                    close_brace_idx = i
                    break
                depth -= 1
        
        if open_brace_idx != -1 and close_brace_idx != -1:
            start_line = get_line_number(content, open_brace_idx)
            end_line = get_line_number(content, close_brace_idx)
            results[tc_id] = {"sl": start_line, "el": end_line}

    return json.dumps(results, indent=2)

if __name__ == "__main__":
    print(tool_list_test_cases())
