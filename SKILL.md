---
name: rr-niche-finder
description: Find untapped rank-and-rent (website landlord) niche + city combinations for local lead generation. Research low-competition local service niches, identify profitable cities/suburbs, calculate lead values, and output ranked opportunity cards. Use when the user wants to find new rank-and-rent niches, research local lead generation opportunities, evaluate city + service combinations for SEO ranking potential, or produce weekly batches of website landlord opportunities.
---

# rr-niche-finder

Find profitable, low-competition niche + city combinations for the rank-and-rent (website landlord) business model.

## What It Does
1. Researches untapped local service niches via web search
2. Identifies mid-size cities and suburbs with weak competition
3. Evaluates search volume, competition level, and lead value
4. Produces ranked **Opportunity Cards** with action plans

## Output Format
Each opportunity includes:
- **Niche + City** (e.g., "crawl space encapsulation in Wichita Kansas")
- **Search Volume** (estimated monthly searches)
- **Competition Level** (Low / Medium / High)
- **Average Job Value** (what the service provider charges)
- **Estimated Lead Value** (what to charge per lead/month)
- **Recommended Monthly Fee** (what to charge the business owner)
- **Domain Suggestion** (available domain idea)
- **Build Priority** (Start Now / Research Further / Monitor)
- **Action Plan** (next 3 steps)

## Workflow

### Step 1: Niche Discovery
Use `scripts/find-niches.py` to search for untapped niches:
```bash
python3 scripts/find-niches.py --category "emergency-services" --count 10
```

Or manually search using these patterns:
- Search: `"[service] + [city]"` competition analysis
- Check: Are top results 2005-era sites?
- Check: Map Pack — are there 3+ strong GMB listings?

### Step 2: City Selection
Target criteria (from `references/city-framework.md`):
- Population: 50K-500K (mid-size cities)
- Avoid: Major metros (NYC, LA, Chicago, Houston)
- Prefer: Suburbs of major metros, residential areas
- Check: Google Map Pack competition

### Step 3: Lead Value Calculation
Use the formula from Kyle (rentlocalsites.com):
```
Lead Value = (Average Job Value × Close Rate) / Leads Per Job
Monthly Fee = Lead Value × Expected Monthly Leads × 0.3-0.5
```

### Step 4: Competition Verification
Use web search or Ahrefs/Mangools (if available):
- Search volume target: 20-100/month
- Keyword difficulty target: <20
- Backlink count of top 3 competitors: <50 each

### Step 5: Output Opportunity Cards
Format as markdown table or structured list. Save to dated file.

## Categories to Rotate Through

| Category | Examples | Seasonality |
|----------|----------|-------------|
| Emergency Services | Water damage, burst pipes, biohazard | Year-round, spikes in storms |
| Specialty Trades | Epoxy flooring, spray foam, crawl space | Year-round |
| Professional Services | Workers comp attorney, tax resolution | Year-round |
| Home Services | Pet cremation, accessibility remodel | Year-round |
| B2B Services | Commercial cleaning, IT support | Year-round |
| Seasonal Services | Holiday lights, snow removal, lawn care | Seasonal |
| Aging-in-Place | Stairlifts, walk-in tubs, ramps | Growing trend |
| Green/Eco | Solar, EV chargers, water filtration | Growing trend |

## Key Principles

### The "Joe, Bill & Steve" Test
> Compete against small local businesses with 2005-era websites, not franchises with $50K/month SEO budgets.

### The Million Combinations Math
> 1,000 niches × 1,000 cities = 1,000,000 combinations. Market is NOT efficient.

### Undercharge for Longevity
> Charge 30-50% of lead value. $600/month for 5 years > $1,500/month for 6 months.

### Do the Hard Thing First
> Ranking is the hard part. Everything after is gravy.

## Scripts

- `scripts/find-niches.py` — Search for untapped niches by category
- `scripts/evaluate-city.py` — Check competition for niche+city combo
- `scripts/calculate-value.py` — Calculate lead value and monthly fee

## References

- `references/niche-database.md` — Curated list of 200+ niches with job values
- `references/city-framework.md` — City selection criteria and methodology
- `references/kyle-insights.md` — Key insights from Kyle's podcast and site

## Weekly Batch Output

The sub-agent should produce:
1. **5-10 Opportunity Cards** — ranked by opportunity score
2. **Summary Table** — all opportunities in one view
3. **Weekly Report** — saved to `~/Obsidian/Penelopi/RankRent/YYYY-MM-DD-batch.md`

## Opportunity Score Formula
```
Score = (Monthly Fee Potential × 0.4) + (Low Competition × 0.3) + (Job Urgency × 0.2) + (Recurring Potential × 0.1)
```
