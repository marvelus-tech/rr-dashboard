#!/usr/bin/env python3
"""
Clean re-scoring of all opportunities with location-industry fit.
This script reads the existing database and applies realistic scoring.
"""
import json
import sys

# Location-industry fit rules
YOUNG_CITIES = {'aurora il', 'aurora co', 'irvine ca', 'plano tx', 'frisco tx', 
    'gilbert az', 'chandler az', 'peoria az', 'cary nc', 'overland park ks',
    'sioux falls sd', 'provo ut', 'orem ut', 'lehi ut', 'boulder co',
    'cambridge ma', 'ann arbor mi', 'madison wi', 'columbia mo', 'college station tx',
    'denton tx'}

RETIREMENT_CITIES = {'the villages fl', 'prescott az', 'sarasota fl', 'naples fl', 
    'scottsdale az', 'st. george ut', 'asheville nc', 'myrtle beach sc',
    'venice fl', 'ocala fl', 'port st. lucie fl', 'cape coral fl',
    'hialeah fl', 'miami gardens fl', 'hollywood fl', 'pembroke pines fl',
    'sunrise fl', 'deerfield beach fl', 'boynton beach fl', 'delray beach fl'}

RESIDENTIAL_SUBURBS = {'blue mountains nsw', 'blacktown nsw', 'penrith nsw', 'campbelltown nsw',
    'frankston vic', 'mornington vic', 'berwick vic', 'craigieburn vic',
    'gold coast qld', 'sunshine coast qld', 'mandurah wa', 'albany wa'}

FREIGHT_CORRIDORS = {'penrith nsw', 'wagga wagga nsw', 'dubbo nsw', 'albury nsw',
    'wodonga vic', 'ballarat vic', 'bendigo vic', 'shepparton vic',
    'toowoomba qld', 'ipswich qld', 'geraldton wa', 'kalgoorlie wa'}

def apply_location_fit(opportunity):
    """Apply location-industry fit penalty/boost to an opportunity."""
    niche = opportunity['niche'].lower()
    city = opportunity['city'].lower()
    score = opportunity.get('opportunity_score', 0)
    
    # Normalize score to 0-100 if needed
    if score <= 10:
        score *= 10
    
    location_fit = 1.0
    penalty_reason = ""
    
    # Trucking attorney needs freight corridors
    if 'trucking' in niche or 'truck' in niche:
        if any(x in city for x in ['mountain', 'blue mountains', 'coast', 'beach', 'village']):
            location_fit = 0.2
            penalty_reason = "Trucking niche in non-freight corridor"
        elif city not in FREIGHT_CORRIDORS:
            location_fit = 0.5
            penalty_reason = "Not a major freight corridor"
    
    # Senior services need retirement cities
    elif any(x in niche for x in ['walk-in tub', 'stairlift', 'senior', 'aging', 'accessibility', 'walk-in shower', 'bathroom accessibility']):
        if city in YOUNG_CITIES:
            location_fit = 0.3
            penalty_reason = "Senior service in young city (median age <35)"
        elif city in RETIREMENT_CITIES:
            location_fit = 1.2
            penalty_reason = "Senior service in retirement destination"
    
    # B2B services need business districts
    elif any(x in niche for x in ['cybersecurity', 'fractional cfo', 'msp', 'commercial cleaning', 'commercial pest', 
                    'business coaching', 'payroll', 'bookkeeping', 'it support', 'records management',
                    'fleet washing', 'commercial', 'industrial']):
        if city in RESIDENTIAL_SUBURBS:
            location_fit = 0.4
            penalty_reason = "B2B niche in residential suburb"
    
    # Foundation repair needs older housing
    elif 'foundation' in niche:
        if any(x in city for x in ['irvine', 'plano', 'frisco', 'gilbert', 'chandler', 'new']):
            location_fit = 0.6
            penalty_reason = "New construction city = less foundation issues"
    
    # Water damage needs flood-prone areas
    elif any(x in niche for x in ['water damage', 'storm damage', 'flood']):
        if any(x in city for x in ['desert', 'phoenix', 'tucson', 'vegas']):
            location_fit = 0.4
            penalty_reason = "Desert city = minimal water damage risk"
    
    # Home battery backup needs solar-friendly cities
    elif 'home battery' in niche or 'battery backup' in niche:
        if any(x in city for x in ['seattle', 'portland', 'chicago', 'detroit', 'minneapolis']):
            location_fit = 0.5
            penalty_reason = "Low solar adoption city"
    
    adjusted_score = min(100, score * location_fit)
    
    return {
        'adjusted_score': round(adjusted_score, 1),
        'location_fit': location_fit,
        'penalty_reason': penalty_reason
    }

def main():
    with open('data/all-batches.json', 'r') as f:
        data = json.load(f)
    
    all_ops = []
    for batch in data['batches']:
        for op in batch['opportunities']:
            fit_result = apply_location_fit(op)
            op['adjusted_score'] = fit_result['adjusted_score']
            op['location_fit'] = fit_result['location_fit']
            op['penalty_reason'] = fit_result['penalty_reason']
            all_ops.append(op)
    
    # Sort by adjusted score
    all_ops.sort(key=lambda x: x.get('adjusted_score', 0), reverse=True)
    
    print('▶ TOP 15 REAL OPPORTUNITIES (Location-Industry Fit Applied)')
    print(f"{'#':<4} {'Niche':<35} {'City':<20} {'Base':<6} {'Adj':<6} {'Fit':<5} {'Fee':<7} {'KD':<4} {'Vol':<5} {'Urg':<4} {'Note'}")
    print('─' * 120)
    
    for i, op in enumerate(all_ops[:15], 1):
        base = op.get('opportunity_score', 0)
        if base <= 10:
            base *= 10
        adj = op.get('adjusted_score', 0)
        fit = op.get('location_fit', 1.0)
        fee = op.get('monthly_fee', 0)
        kd = op.get('seo', {}).get('keyword_difficulty', 'N/A')
        vol = op.get('seo', {}).get('search_volume', 'N/A')
        urg = op.get('urgency', 'N/A')
        note = op.get('penalty_reason', '')
        
        print(f"{i:<4} {op['niche'][:34]:<35} | {op['city'][:19]:<20} | {base:<6} | {adj:<6} | {fit:<5} | ${fee:<6.0f} | {kd:<4} | {vol:<5} | {urg:<4} | {note}")
    
    print()
    print('▶ FALSE POSITIVES EXPOSED (Base >80, Adjusted <50)')
    for op in all_ops:
        base = op.get('opportunity_score', 0)
        if base <= 10:
            base *= 10
        adj = op.get('adjusted_score', 0)
        if base > 80 and adj < 50:
            print(f"  - {op['niche']} in {op['city']}: {base} -> {adj} (fit: {op.get('location_fit', 1.0)}) - {op.get('penalty_reason', '')}")
    
    print()
    print('▶ SCORE DISTRIBUTION')
    print(f"  Start Now (70+):       {sum(1 for x in all_ops if x.get('adjusted_score', 0) >= 70)}")
    print(f"  Research Further (50+): {sum(1 for x in all_ops if 50 <= x.get('adjusted_score', 0) < 70)}")
    print(f"  Monitor (30+):         {sum(1 for x in all_ops if 30 <= x.get('adjusted_score', 0) < 50)}")
    print(f"  Low Priority (<30):    {sum(1 for x in all_ops if x.get('adjusted_score', 0) < 30)}")
    
    # Save updated database
    with open('data/all-batches-rescored.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print()
    print("Saved rescored database to data/all-batches-rescored.json")

if __name__ == '__main__':
    main()
