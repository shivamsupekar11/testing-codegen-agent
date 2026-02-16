"""
csv_excel_to_toon.py — Convert CSV/Excel test cases to JSON and TOON format
                       in batches of BATCH_SIZE (default 20).

Each run:
  1. Reads ALL test cases from the Excel/CSV input file.
  2. Determines the current batch offset from `.batch_state`.
  3. If a TOON file from a previous batch exists, moves it to
     `workspace/intermediate/archive/` with a timestamp.
  4. Writes a new JSON + TOON for the current batch of test cases.
  5. Updates `.batch_state` to point to the next batch.

Usage:
    python csv_excel_to_toon.py              # Process the next batch of 20
    python csv_excel_to_toon.py --reset      # Reset batch state and start over
    python csv_excel_to_toon.py --all        # Process ALL batches, archiving each one
"""

import json
import os
import shutil
import sys
import time
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────
BATCH_SIZE = 20

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


# ── Batch state helpers ───────────────────────────────────────────────

def _batch_state_path(intermediate_dir: str) -> str:
    """Return the path to the batch state file."""
    return os.path.join(intermediate_dir, ".batch_state")


def read_batch_offset(intermediate_dir: str) -> int:
    """Read the current batch offset (number of TCs already processed)."""
    path = _batch_state_path(intermediate_dir)
    if os.path.isfile(path):
        try:
            with open(path, "r") as f:
                return int(f.read().strip())
        except (ValueError, OSError):
            return 0
    return 0


def write_batch_offset(intermediate_dir: str, offset: int) -> None:
    """Write the current batch offset to disk."""
    path = _batch_state_path(intermediate_dir)
    with open(path, "w") as f:
        f.write(str(offset))


def reset_batch_state(intermediate_dir: str) -> None:
    """Reset the batch offset to 0."""
    write_batch_offset(intermediate_dir, 0)
    print("🔄 Batch state reset to 0.")


# ── Archive helper ────────────────────────────────────────────────────

def archive_existing_toon(intermediate_dir: str, toon_file: str, batch_label: str = None) -> None:
    """Move the existing TOON (and its JSON) to the archive folder."""
    archive_dir = os.path.join(intermediate_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for ext in (".toon", ".json"):
        src = os.path.join(intermediate_dir, os.path.splitext(toon_file)[0] + ext)
        if os.path.isfile(src):
            base = os.path.splitext(os.path.basename(src))[0]
            if batch_label:
                dest = os.path.join(archive_dir, f"{base}_{batch_label}_{timestamp}{ext}")
            else:
                dest = os.path.join(archive_dir, f"{base}_{timestamp}{ext}")
            shutil.move(src, dest)
            print(f"📦 Archived: {os.path.basename(src)} → archive/{os.path.basename(dest)}")


# ── Slice test cases from the full dataset ────────────────────────────

def slice_test_cases(all_modules: list, offset: int, batch_size: int) -> tuple:
    """
    Given the full list of module dicts (each with 'test_cases'), return:
      - A new module list containing only the TCs in [offset, offset+batch_size)
      - The total number of test cases across all modules
      - The number of TCs in this batch
    """
    # Flatten all TCs keeping their module info
    flat_tcs = []
    for mod in all_modules:
        for tc in mod["test_cases"]:
            flat_tcs.append((mod["module"], tc))

    total = len(flat_tcs)
    batch_tcs = flat_tcs[offset: offset + batch_size]
    batch_count = len(batch_tcs)

    # Rebuild module structure for this batch
    from collections import OrderedDict
    modules = OrderedDict()
    for module_name, tc in batch_tcs:
        modules.setdefault(module_name, []).append(tc)

    batch_modules = [{"module": m, "test_cases": tcs} for m, tcs in modules.items()]
    return batch_modules, total, batch_count


# ── Process a single batch ────────────────────────────────────────────

def process_batch(all_data, offset, batch_size, output_dir, base_name, batch_num, total_batches, total_tcs):
    """Process a single batch of test cases."""
    
    # Slice the current batch
    batch_data, total, batch_count = slice_test_cases(all_data, offset, batch_size)
    
    print(f"\n📊 Batch {batch_num}/{total_batches} — TCs {offset + 1} to {offset + batch_count} (of {total} total)")
    print(f"   Batch size: {batch_size} | This batch: {batch_count} TCs\n")
    
    json_output_file = os.path.join(output_dir, base_name + ".json")
    toon_output_file = os.path.join(output_dir, base_name + ".toon")
    
    # Save as JSON
    print(f"💾 Saving JSON to: {json_output_file}")
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=2, ensure_ascii=False)
    
    # Convert to TOON and save
    print(f"🔄 Converting to TOON format...")
    try:
        toon_str = TOON_MODULE.encode(batch_data)
        
        print(f"💾 Saving TOON to: {toon_output_file}")
        with open(toon_output_file, "w", encoding="utf-8") as f:
            f.write(toon_str)
            
    except Exception as e:
        print(f"❌ Error encoding to TOON format: {e}")
        if "TOON encoder is not yet implemented" in str(e):
            print("The installed 'toon-format' library seems to be incomplete. Try 'pip install toon-python'.")
        sys.exit(1)
    
    print(f"✅ Batch {batch_num} complete — {batch_count} TCs written.")
    
    return batch_count


# ── Main ──────────────────────────────────────────────────────────────

def main():
    # Handle --reset flag
    if "--reset" in sys.argv:
        ENV_PATH = os.path.join(REPO_ROOT, ".env")
        env = load_env(ENV_PATH)
        INTERMEDIATE_DIR = env.get("INTERMEDIATE_DIR", "").strip()
        if INTERMEDIATE_DIR and not os.path.isabs(INTERMEDIATE_DIR):
            INTERMEDIATE_DIR = os.path.join(REPO_ROOT, INTERMEDIATE_DIR)
        reset_batch_state(INTERMEDIATE_DIR)
        return

    # Check if --all flag is present
    process_all = "--all" in sys.argv

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
        all_data = convert(rows)
    except Exception as e:
        print(f"❌ Error converting file: {e}")
        sys.exit(1)

    # Prepare output directory
    if INTERMEDIATE_DIR and not os.path.exists(INTERMEDIATE_DIR):
        os.makedirs(INTERMEDIATE_DIR, exist_ok=True)

    output_dir = INTERMEDIATE_DIR if INTERMEDIATE_DIR and os.path.isdir(INTERMEDIATE_DIR) else INPUT_DIR
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Count total TCs
    total_tcs = sum(len(m["test_cases"]) for m in all_data)
    total_batches = (total_tcs + BATCH_SIZE - 1) // BATCH_SIZE

    if process_all:
        # Process ALL batches, archiving each one
        print(f"\n📊 Processing ALL {total_tcs} test cases in {total_batches} batches")
        print(f"   Each batch will be archived separately\n")
        
        # Reset batch state
        reset_batch_state(output_dir)
        
        offset = 0
        batch_num = 1
        
        while offset < total_tcs:
            # Process current batch
            batch_count = process_batch(
                all_data, offset, BATCH_SIZE, output_dir, base_name, 
                batch_num, total_batches, total_tcs
            )
            
            # Archive the batch files we just created
            batch_label = f"batch{batch_num}_TCs{offset+1}-{offset+batch_count}"
            print(f"\n📦 Archiving Batch {batch_num}...")
            archive_existing_toon(output_dir, base_name + ".toon", batch_label)
            
            # Move to next batch
            offset += batch_count
            batch_num += 1
            
            # Small delay between batches to ensure unique timestamps
            if offset < total_tcs:
                time.sleep(0.1)
        
        print(f"\n🎉 All {total_tcs} test cases processed and archived in {total_batches} batches!")
        print(f"   Check the archive folder: {os.path.join(output_dir, 'archive')}")
        
    else:
        # Single batch mode (existing behavior)
        offset = read_batch_offset(output_dir)

        if offset >= total_tcs:
            print(f"✅ All {total_tcs} test cases have been processed across all batches.")
            print(f"   Run with --reset to start over, or --all to process everything at once.")
            return

        # Archive existing TOON/JSON if this is NOT the first batch
        if offset > 0:
            archive_existing_toon(output_dir, base_name + ".toon")

        # Process current batch
        batch_num = (offset // BATCH_SIZE) + 1
        batch_count = process_batch(
            all_data, offset, BATCH_SIZE, output_dir, base_name,
            batch_num, total_batches, total_tcs
        )

        # Update batch offset for next run
        new_offset = offset + batch_count
        write_batch_offset(output_dir, new_offset)

        remaining = total_tcs - new_offset
        if remaining > 0:
            print(f"📋 {remaining} TCs remaining. Run the script again for the next batch.")
        else:
            print(f"🎉 All {total_tcs} test cases have been processed!")
            print(f"   Run with --reset to start over.")


if __name__ == "__main__":
    main()