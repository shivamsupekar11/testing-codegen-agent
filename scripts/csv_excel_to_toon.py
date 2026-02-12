"""
csv_excel_to_toon.py — Convert CSV/Excel test cases to JSON and TOON format.
Reads INPUT_DIR from agent_analyzer/.env to find the input file.
Saves output JSON and TOON files to INTERMEDIATE_DIR.
"""

import json
import os
import sys

# Ensure script directory is in sys.path to allow importing sibling modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

try:
    import toon_python
    TOON_MODULE = toon_python
except ImportError:
    try:
        import toon_format
        TOON_MODULE = toon_format
    except ImportError:
        print("❌ toon-python or toon-format library not found.")
        print("Please install it using: pip install toon-python")
        sys.exit(1)

# Import necessary functions from csv_excel_to_json.py
try:
    from csv_excel_to_json import load_env, find_input_file, read_file, convert, REPO_ROOT
except ImportError:
    print("❌ Could not import from csv_excel_to_json.py. Make sure it exists in the same directory.")
    sys.exit(1)

def main():
    # 1. Load configuration from .env
    ENV_PATH = os.path.join(REPO_ROOT, ".env")
    env = load_env(ENV_PATH)
    
    INPUT_DIR = env.get("INPUT_DIR", "").strip()
    INTERMEDIATE_DIR = env.get("INTERMEDIATE_DIR", "").strip()

    # Resolve paths relative to REPO_ROOT if they are not absolute
    if INPUT_DIR and not os.path.isabs(INPUT_DIR):
        INPUT_DIR = os.path.join(REPO_ROOT, INPUT_DIR)
    if INTERMEDIATE_DIR and not os.path.isabs(INTERMEDIATE_DIR):
        INTERMEDIATE_DIR = os.path.join(REPO_ROOT, INTERMEDIATE_DIR)

    if not INPUT_DIR or not os.path.isdir(INPUT_DIR):
        print(f"❌ INPUT_DIR not set or invalid in {ENV_PATH}")
        sys.exit(1)

    # 2. Find and read input file
    input_file = find_input_file(INPUT_DIR)
    if not input_file:
        print(f"❌ No .csv or .xlsx file found in INPUT_DIR: {INPUT_DIR}")
        sys.exit(1)

    print(f"📂 Input  : {input_file}")
    
    try:
        rows = read_file(input_file)
        data = convert(rows)
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        sys.exit(1)

    # Prepare output paths
    if INTERMEDIATE_DIR and not os.path.exists(INTERMEDIATE_DIR):
        os.makedirs(INTERMEDIATE_DIR, exist_ok=True)
    
    # Use INTERMEDIATE_DIR for output, fallback to INPUT_DIR
    output_dir = INTERMEDIATE_DIR if INTERMEDIATE_DIR and os.path.isdir(INTERMEDIATE_DIR) else INPUT_DIR
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    json_output_file = os.path.join(output_dir, base_name + ".json")
    toon_output_file = os.path.join(output_dir, base_name + ".toon")

    # 3. Save as JSON
    print(f"💾 Saving JSON to: {json_output_file}")
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 4. Convert to TOON and save
    print(f"🔄 Converting to TOON format...")
    try:
        toon_str = TOON_MODULE.encode(data)
        
        print(f"💾 Saving TOON to: {toon_output_file}")
        with open(toon_output_file, "w", encoding="utf-8") as f:
            f.write(toon_str)
            
    except Exception as e:
        print(f"❌ Error encoding to TOON format: {e}")
        if "TOON encoder is not yet implemented" in str(e):
             print("The installed 'toon-format' library seems to be incomplete. Try 'pip install toon-python'.")
        sys.exit(1)

    print("✅ Conversion complete.")

if __name__ == "__main__":
    main()
