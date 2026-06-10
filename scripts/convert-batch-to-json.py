#!/usr/bin/env python3
"""
Convert find-niches.py markdown output to JSON.
Usage: python3 convert-batch-to-json.py <input.md> <output.json>
"""
import re
import json
import sys
import argparse

def parse_markdown_batch(filepath):
    """Parse the markdown batch file and extract opportunities as structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    opportunities = []
    
    # Find all opportunity card sections
    # Pattern: ### #N: [niche] in [city]\n\n(body until next ### #N+1: or end)
    card_pattern = r'###\s*#(\d+):\s*(.+?)\s+in\s+(.+?)\n\n(.+?)(?=\n###\s*#\d+:|\Z)'
    
    for match in re.finditer(card_pattern, content, re.DOTALL):
        rank = int(match.group(1))
        niche = match.group(2).strip()
        city = match.group(3).strip()
        body = match.group(4)
        
        # Extract fields using regex
        def extract_field(pattern, text, default=""):
            m = re.search(pattern, text)
            return m.group(1).strip() if m else default
        
        avg_job_value = extract_field(r'\*\*Average Job Value:\*\*\s*\$?([\d,]+)', body)
        lead_value = extract_field(r'\*\*Estimated Lead Value:\*\*\s*\$?([\d,]+)', body)
        monthly_fee = extract_field(r'\*\*Recommended Monthly Fee:\*\*\s*\$?([\d,]+)', body)
        urgency = extract_field(r'\*\*Urgency Level:\*\*\s*(\d+)/10', body)
        recurring = extract_field(r'\*\*Recurring Potential:\*\*\s*(Yes|No)', body)
        score = extract_field(r'\*\*Opportunity Score:\*\*\s*([\d.]+)/10', body)
        priority = extract_field(r'\*\*Priority:\*\*\s*(.+?)\n', body)
        notes = extract_field(r'\*\*Notes:\*\*\s*(.+?)\n', body)
        urgency_reason = extract_field(r'\*\*Urgency Reason:\*\*\s*(.+?)\n', body)
        location_reasoning = extract_field(r'\*\*Location Reasoning:\*\*\s*(.+?)\n', body)
        
        # Extract domains from the dedicated Domain Suggestions section first
        domain_block = extract_field(r'\*\*Domain Suggestions:\*\*\s*(.+?)(?=\n\n\*\*Action Plan:\*\*|\n\*\*Action Plan:\*\*|\Z)', body)
        domains = re.findall(r'`([^`]+\.(?:com|net|org|io|co))`', domain_block)
        if not domains:
            # Fallback for older markdown formats
            domains = re.findall(r'`([^`]+\.(?:com|net|org|io|co))`', body)
        
        # Extract action plan
        actions = re.findall(r'\d+\.\s*(.+?)(?=\n|$)', body)
        
        # Clean up numeric values
        def clean_num(s):
            return int(s.replace(',', '')) if s else 0
        
        # Extract SEO metrics
        seo = {}
        seo_fields = {
            'search_volume': r'\*\*Search Volume:\*\*\s*(\d+)',
            'keyword_difficulty': r'\*\*Keyword Difficulty:\*\*\s*(\d+)',
            'competition_level': r'\*\*Competition Level:\*\*\s*(.+?)\n',
            'backlink_estimate': r'\*\*Backlink Estimate:\*\*\s*(.+?)\n',
            'map_pack_status': r'\*\*Map Pack Status:\*\*\s*(.+?)\n',
            'competitor_da': r'\*\*Top Competitor DA:\*\*\s*(\d+)',
            'content_gap_score': r'\*\*Content Gap Score:\*\*\s*(\d+)',
            'seo_opportunity_score': r'\*\*SEO Opportunity Score:\*\*\s*(\d+)',
        }
        for key, pattern in seo_fields.items():
            m = re.search(pattern, body)
            if m:
                val = m.group(1).strip()
                if key in ['search_volume', 'keyword_difficulty', 'competitor_da', 'content_gap_score', 'seo_opportunity_score']:
                    seo[key] = int(val)
                else:
                    seo[key] = val
        
        # Extract status
        status = extract_field(r'\*\*Status:\*\*\s*(.+?)\n', body)
        if not status:
            status = "New"
        
        # Extract web prompt from hidden HTML comment
        web_prompt_match = re.search(r'<!--WEB_PROMPT-->(.+?)<!--/WEB_PROMPT-->', body, re.DOTALL)
        web_prompt = web_prompt_match.group(1).strip() if web_prompt_match else ""
        
        opportunities.append({
            "niche": niche,
            "city": city,
            "avg_job_value": clean_num(avg_job_value),
            "lead_value": clean_num(lead_value),
            "monthly_fee": clean_num(monthly_fee),
            "urgency": int(urgency) if urgency else 5,
            "urgency_reason": urgency_reason,
            "recurring": recurring == "Yes",
            "opportunity_score": float(score) if score else 0,
            "priority": priority,
            "status": status,
            "notes": notes,
            "location_reasoning": location_reasoning,
            "domain_suggestions": domains,
            "action_plan": [a.strip() for a in actions if a.strip()],
            "seo": seo,
            "web_prompt": web_prompt
        })
    
    return opportunities

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output JSON file")
    args = parser.parse_args()
    
    opportunities = parse_markdown_batch(args.input)
    
    output = {
        "generated_at": datetime.now().isoformat(),
        "count": len(opportunities),
        "opportunities": opportunities
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Converted {len(opportunities)} opportunities to JSON: {args.output}")

if __name__ == "__main__":
    from datetime import datetime
    main()
