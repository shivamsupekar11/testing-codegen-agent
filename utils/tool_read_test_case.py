import json
import sys
import subprocess
import os

TEMP_JSON_FILE = "workspace/intermediate/temp_tc.json"

def tool_read_test_case(tc_id_arg: str):
    """
    Parses the JSON file, filters for test cases, saves them to a temporary JSON file,
    runs the TOON CLI converter on it, and returns the TOON output string.
    """
    file_path = "workspace/intermediate/test_cases_template_output.json"
    
    # Normalize input to a list of IDs
    if isinstance(tc_id_arg, list):
        target_ids = tc_id_arg
    else:
        target_ids = [tid.strip() for tid in tc_id_arg.split(',')]

    with open(file_path, 'r') as f:
        data = json.load(f)
        
    results = []
    
    for module in data:
        for tc in module.get("test_cases", []):
            if tc.get("tc_id") in target_ids:
                toon_tc = {
                    "tc_id": tc.get("tc_id", ""),
                    "title": tc.get("title", ""),
                    "description": tc.get("description", ""),
                    "priority": tc.get("priority", ""),
                    "test_type": tc.get("test_type", ""),
                    "preconditions": tc.get("preconditions", ""),
                    "steps": []
                }
                
                for step in tc.get("steps", []):
                    resolved = step.get("resolved_locators", {})
                    assertion = step.get("assertion", {})
                    
                    toon_step = {
                        "step_no": step.get("step_no"),
                        "action": step.get("action", ""),
                        "element_type": step.get("element_type", ""),
                        "original_hint": step.get("original_hint", ""),
                        "resolved_locators": {
                            "value": resolved.get("value", ""),
                            "confidence": resolved.get("confidence", 0),
                            "xpath": resolved.get("xpath", ""),
                            "fallbacks": resolved.get("fallbacks", []) if isinstance(resolved.get("fallbacks"), list) else [] 
                        },
                        "input_data": step.get("input_data"),
                        "expected_result": step.get("expected_result", ""),
                        "assertion": {
                            "type": assertion.get("type", ""),
                            "target": assertion.get("target"),
                            "value": assertion.get("value")
                        },
                        "method_name": step.get("method_name", "")
                    }
                    toon_tc["steps"].append(toon_step)
                
                results.append(toon_tc)

    # Save to temp JSON file
    with open(TEMP_JSON_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    # Run npx command to convert to TOON
    try:
        # Use shell=True to ensure npx is found in path environment properly
        result = subprocess.run(
            f"npx -y @toon-format/cli {TEMP_JSON_FILE}", 
            shell=True, 
            capture_output=True, 
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error converting to TOON: {e.stderr}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(tool_read_test_case(sys.argv[1]))
    else:
        print("Usage: python read_test_case.py TC_ID")
