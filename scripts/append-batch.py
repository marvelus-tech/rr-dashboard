#!/usr/bin/env python3
"""
Append latest batch to cumulative database and regenerate dashboard.
Filters out any IDs archived in killed/*.json files.
"""
import json
import sys
import os
import glob
from datetime import datetime
import subprocess

DATA_DIR = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/data"
LATEST_JSON = f"{DATA_DIR}/latest-batch.json"
ALL_BATCHES_JSON = f"{DATA_DIR}/all-batches.json"
DASHBOARD_HTML = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/dashboard.html"
KILLED_DIR = "/Users/oktos/.openclaw/workspace/skills/rr-niche-finder/killed"

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_killed_ids():
    """Load all killed opportunity IDs from killed/*.json archives"""
    killed_ids = set()
    
    if not os.path.exists(KILLED_DIR):
        return killed_ids
    
    for archive_path in glob.glob(os.path.join(KILLED_DIR, "*.json")):
        try:
            with open(archive_path, 'r') as f:
                archive = json.load(f)
                if "ids" in archive and isinstance(archive["ids"], list):
                    killed_ids.update(archive["ids"])
                    print(f"📋 Loaded {len(archive['ids'])} killed IDs from {os.path.basename(archive_path)}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ Could not load {archive_path}: {e}")
    
    return killed_ids

def generate_opportunity_id(op):
    """Generate slug-style ID from niche and city (matches dashboard generator)"""
    niche = op.get('niche', '').lower().strip()
    city = op.get('city', '').lower().strip()
    slug = f"{niche}-{city}".replace(' ', '-').replace('.', '')
    return slug

def main():
    # Load killed IDs
    killed_ids = load_killed_ids()
    if killed_ids:
        print(f"🚫 Will skip {len(killed_ids)} archived slop IDs")
    
    # Load latest batch
    try:
        with open(LATEST_JSON, 'r') as f:
            latest = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {LATEST_JSON} not found. Run find-niches.py first.")
        sys.exit(1)
    
    # Filter out killed opportunities
    raw_opportunities = latest.get("opportunities", [])
    filtered_opportunities = []
    skipped_count = 0
    
    for op in raw_opportunities:
        op_id = generate_opportunity_id(op)
        if op_id in killed_ids:
            print(f"  ⏭️  Skipping killed ID: {op_id}")
            skipped_count += 1
        else:
            filtered_opportunities.append(op)
    
    if skipped_count > 0:
        print(f"✓ Filtered out {skipped_count} killed opportunities from new batch")
    
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
        "opportunities": filtered_opportunities
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
