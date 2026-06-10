#!/usr/bin/env python3
"""
Append latest batch to cumulative database and regenerate dashboard.
"""
import json
import sys
from datetime import datetime
import subprocess

DATA_DIR = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/data"
LATEST_JSON = f"{DATA_DIR}/latest-batch.json"
ALL_BATCHES_JSON = f"{DATA_DIR}/all-batches.json"
DASHBOARD_HTML = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/dashboard.html"

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Load latest batch
    try:
        with open(LATEST_JSON, 'r') as f:
            latest = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {LATEST_JSON} not found. Run find-niches.py first.")
        sys.exit(1)
    
    # Load cumulative database
    try:
        with open(ALL_BATCHES_JSON, 'r') as f:
            all_batches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_batches = {"batches": []}
    
    # Add batch metadata
    batch_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "week": len(all_batches.get("batches", [])) + 1,
        "opportunities": latest.get("opportunities", [])
    }
    
    all_batches["batches"].append(batch_entry)
    
    # Save cumulative database
    with open(ALL_BATCHES_JSON, 'w') as f:
        json.dump(all_batches, f, indent=2)
    
    print(f"✅ Appended batch #{batch_entry['week']} with {len(batch_entry['opportunities'])} opportunities")
    print(f"📊 Total batches in database: {len(all_batches['batches'])}")
    
    # Regenerate dashboard
    print("🎨 Regenerating dashboard...")
    result = subprocess.run(
        ["python3", "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/scripts/generate-dashboard.py"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Dashboard regenerated: {DASHBOARD_HTML}")
    else:
        print(f"⚠️ Dashboard generation had issues: {result.stderr}")
    
    return all_batches

if __name__ == "__main__":
    main()
