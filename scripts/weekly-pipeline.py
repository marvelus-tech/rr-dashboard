#!/usr/bin/env python3
"""
Master weekly pipeline script.
Orchestrates the entire workflow: generate batch -> convert to JSON -> append -> regenerate dashboard.
"""
import subprocess
import sys
import os
from datetime import datetime

SKILL_DIR = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder"
DATA_DIR = f"{SKILL_DIR}/data"

def run_cmd(cmd, description):
    """Run a shell command and report status."""
    print(f"\n🔧 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FAILED: {result.stderr}")
        return False
    print(result.stdout.strip() if result.stdout else "✅ Done")
    return True

def main():
    print("=" * 60)
    print("🚀 Rank & Rent Weekly Pipeline")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Initialize all-batches.json if empty
    all_batches_path = f"{DATA_DIR}/all-batches.json"
    if not os.path.exists(all_batches_path) or os.path.getsize(all_batches_path) < 10:
        with open(all_batches_path, 'w') as f:
            f.write('{"batches": []}')
        print("📂 Initialized empty batch database")
    
    # Step 1: Generate batch
    md_path = "/tmp/weekly-batch.md"
    json_path = f"{DATA_DIR}/latest-batch.json"
    
    if not run_cmd(
        f"cd {SKILL_DIR} && python3 scripts/find-niches.py --count 10 --australian --output {md_path}",
        "Generating niche batch"
    ):
        return 1
    
    # Step 2: Convert to JSON
    if not run_cmd(
        f"python3 {SKILL_DIR}/scripts/convert-batch-to-json.py {md_path} {json_path}",
        "Converting to JSON"
    ):
        return 1
    
    # Step 3: Append to cumulative database + regenerate dashboard
    if not run_cmd(
        f"python3 {SKILL_DIR}/scripts/append-batch.py",
        "Appending to database & regenerating dashboard"
    ):
        return 1
    
    print("\n" + "=" * 60)
    print("✅ Weekly pipeline complete!")
    print(f"📊 Dashboard: {SKILL_DIR}/dashboard.html")
    print(f"📁 Markdown: {md_path}")
    print(f"📁 JSON: {json_path}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
