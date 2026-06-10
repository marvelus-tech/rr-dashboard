#!/usr/bin/env python3
"""
Rank & Rent Niche Finder
Generates a weekly batch of niche + city opportunities.
Usage: python3 find-niches.py --category "emergency-services" --count 5
"""
import argparse
import json
import random
import sys
from datetime import datetime


def calculate_seo_metrics(niche, city):
    """Calculate estimated SEO metrics for a niche + city combo.
    In production, these would come from Ahrefs/Mangools API calls."""
    
    avg_value = niche["avg_value"]
    urgency = niche["urgency"]
    
    # Search volume estimation based on niche characteristics
    # Emergency services = higher volume (people search when in need)
    # Specialty trades = moderate volume
    # Professional services = lower volume but higher intent
    if urgency >= 8:
        base_volume = random.randint(40, 120)
    elif urgency >= 5:
        base_volume = random.randint(20, 80)
    else:
        base_volume = random.randint(10, 50)
    
    # Adjust for city size (smaller cities = lower volume)
    # We don't have real population data, so estimate based on city name patterns
    if any(x in city for x in ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]):
        city_multiplier = 3.0
    elif any(x in city for x in ["TX", "CA", "FL", "NY", "IL"]):
        city_multiplier = 1.5
    else:
        city_multiplier = 1.0
    
    search_volume = int(base_volume * city_multiplier)
    
    # Keyword difficulty estimation
    # Higher job value = more competition (more money = more SEO investment)
    # Lower job value = less competition
    if avg_value > 20000:
        base_difficulty = random.randint(35, 65)
    elif avg_value > 10000:
        base_difficulty = random.randint(25, 50)
    elif avg_value > 5000:
        base_difficulty = random.randint(15, 40)
    else:
        base_difficulty = random.randint(5, 25)
    
    # Adjust for urgency (emergency = less competition because fewer people target it)
    if urgency >= 8:
        base_difficulty -= 10
    
    keyword_difficulty = max(5, min(85, base_difficulty))
    
    # Competition level
    if keyword_difficulty < 20:
        competition_level = "Low"
    elif keyword_difficulty < 40:
        competition_level = "Medium"
    else:
        competition_level = "High"
    
    # Backlink estimate (weak = under 50, moderate = 50-200, strong = 200+)
    if keyword_difficulty < 20:
        backlink_estimate = "Weak (0-30)"
    elif keyword_difficulty < 40:
        backlink_estimate = "Moderate (30-100)"
    else:
        backlink_estimate = "Strong (100+)"
    
    # Map pack status (how many GMB listings)
    if keyword_difficulty < 15:
        map_pack_status = "Empty or Weak"
    elif keyword_difficulty < 30:
        map_pack_status = "2-3 Listings"
    else:
        map_pack_status = "Saturated (5+)"
    
    # Domain authority estimate for top competitor
    if keyword_difficulty < 20:
        competitor_da = random.randint(8, 20)
    elif keyword_difficulty < 40:
        competitor_da = random.randint(15, 35)
    else:
        competitor_da = random.randint(30, 55)
    
    # Content gap score (how much content is missing from current rankings)
    # Higher = more opportunity for you
    content_gap = max(10, min(90, 100 - keyword_difficulty + random.randint(-10, 10)))
    
    # Overall SEO opportunity score (0-100)
    # High search volume + low difficulty = great opportunity
    seo_opportunity = min(100, int((search_volume / 2) + (50 - keyword_difficulty)))
    
    # Enhanced scoring: Kyle framework weights
    # Lead Value (2.5x) + Low Competition (2.0x) + Traffic (1.0x) + Urgency (1.5x)
    lead_value_score = min(10, avg_value / 2000)  # $20K = 10, $2K = 1
    competition_score = max(0, 11 - (keyword_difficulty / 10))  # KD 10 = 10, KD 50 = 6
    traffic_score = min(10, search_volume / 15)  # 150 searches = 10, 30 = 2
    urgency_score = urgency / 10  # 10 = 1.0, 5 = 0.5
    
    composite_score = (
        (lead_value_score * 2.5) +
        (competition_score * 2.0) +
        (traffic_score * 1.0) +
        (urgency_score * 1.5)
    )
    
    # Normalize to 0-100 scale
    composite_score = min(100, max(0, int(composite_score * 2.5)))
    
    return {
        "search_volume": search_volume,
        "keyword_difficulty": keyword_difficulty,
        "competition_level": competition_level,
        "backlink_estimate": backlink_estimate,
        "map_pack_status": map_pack_status,
        "competitor_da": competitor_da,
        "content_gap_score": content_gap,
        "composite_score": composite_score,
        "data_source": "estimated",
        "verification_needed": True
    }


# Curated niche database by category
NICHE_DATABASE = {
    "emergency-services": [
        {"name": "Water damage restoration", "avg_value": 3500, "urgency": 10, "recurring": False, "notes": "Target suburbs"},
        {"name": "Burst pipe repair", "avg_value": 1250, "urgency": 10, "recurring": False, "notes": "Winter emergency"},
        {"name": "Sewer line backup", "avg_value": 3250, "urgency": 10, "recurring": False, "notes": "Immediate action"},
        {"name": "Foundation crack repair", "avg_value": 9000, "urgency": 9, "recurring": False, "notes": "Structural panic"},
        {"name": "Mold remediation", "avg_value": 3250, "urgency": 9, "recurring": False, "notes": "Health concern"},
        {"name": "Biohazard cleanup", "avg_value": 5000, "urgency": 9, "recurring": False, "notes": "Very specialized"},
        {"name": "Storm damage repair", "avg_value": 6000, "urgency": 8, "recurring": False, "notes": "Seasonal spikes"},
        {"name": "Hoarding cleanup", "avg_value": 8500, "urgency": 8, "recurring": False, "notes": "Mental + physical"},
        {"name": "Radon remediation", "avg_value": 1900, "urgency": 7, "recurring": False, "notes": "Home sales"},
        {"name": "Asbestos removal", "avg_value": 6000, "urgency": 7, "recurring": False, "notes": "Regulated"},
    ],
    "specialty-trades": [
        {"name": "Crawl space encapsulation", "avg_value": 9000, "urgency": 5, "recurring": False, "notes": "High ticket"},
        {"name": "Epoxy flooring", "avg_value": 5500, "urgency": 4, "recurring": False, "notes": "$50K/mo earner"},
        {"name": "Spray foam insulation", "avg_value": 4000, "urgency": 4, "recurring": False, "notes": "$90K/mo earner"},
        {"name": "Basement waterproofing", "avg_value": 9000, "urgency": 6, "recurring": False, "notes": "High anxiety"},
        {"name": "French drain installation", "avg_value": 6500, "urgency": 5, "recurring": False, "notes": "Water mgmt"},
        {"name": "Outdoor kitchen installation", "avg_value": 30000, "urgency": 3, "recurring": False, "notes": "Premium"},
        {"name": "Generator installation", "avg_value": 12500, "urgency": 5, "recurring": False, "notes": "Power outages"},
        {"name": "EV charger installation", "avg_value": 1750, "urgency": 3, "recurring": False, "notes": "EV growth"},
        {"name": "Home elevator installation", "avg_value": 35000, "urgency": 3, "recurring": False, "notes": "Aging in place"},
        {"name": "Stairlift installation", "avg_value": 6500, "urgency": 4, "recurring": False, "notes": "Medicare"},
        {"name": "Walk-in tub installation", "avg_value": 10000, "urgency": 4, "recurring": False, "notes": "Accessibility"},
        {"name": "Dryer vent cleaning", "avg_value": 350, "urgency": 5, "recurring": True, "notes": "Fire hazard"},
        {"name": "Air duct cleaning", "avg_value": 1000, "urgency": 4, "recurring": True, "notes": "HVAC adjacent"},
        {"name": "Chimney repair", "avg_value": 5500, "urgency": 5, "recurring": False, "notes": "Safety"},
        {"name": "Concrete leveling", "avg_value": 3000, "urgency": 4, "recurring": False, "notes": "Alternative"},
    ],
    "professional-services": [
        {"name": "Workers comp attorney", "avg_value": 27500, "urgency": 6, "recurring": False, "notes": "Kyle's 1st client"},
        {"name": "Social security disability attorney", "avg_value": 9000, "urgency": 5, "recurring": False, "notes": "Federal law"},
        {"name": "Estate planning attorney", "avg_value": 6000, "urgency": 3, "recurring": False, "notes": "Aging pop"},
        {"name": "Tax resolution specialist", "avg_value": 6000, "urgency": 7, "recurring": False, "notes": "IRS problems"},
        {"name": "Trucking accident attorney", "avg_value": 55000, "urgency": 6, "recurring": False, "notes": "High value"},
        {"name": "Veterans benefits attorney", "avg_value": 9000, "urgency": 5, "recurring": False, "notes": "VA claims"},
        {"name": "Elder law attorney", "avg_value": 9000, "urgency": 4, "recurring": False, "notes": "Aging pop"},
        {"name": "Employment law attorney", "avg_value": 27500, "urgency": 5, "recurring": False, "notes": "Wrongful term"},
        {"name": "Business coaching", "avg_value": 11000, "urgency": 3, "recurring": True, "notes": "B2B"},
        {"name": "Fractional CFO", "avg_value": 15000, "urgency": 3, "recurring": True, "notes": "Monthly retainer"},
        {"name": "IT support MSP", "avg_value": 6000, "urgency": 4, "recurring": True, "notes": "Recurring"},
        {"name": "Cybersecurity consulting", "avg_value": 27500, "urgency": 6, "recurring": False, "notes": "Breach-driven"},
        {"name": "Payroll services", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "B2B"},
        {"name": "Bookkeeping", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "B2B"},
        {"name": "Property management", "avg_value": 1250, "urgency": 3, "recurring": True, "notes": "Per property"},
    ],
    "home-services": [
        {"name": "Pet cremation", "avg_value": 1600, "urgency": 5, "recurring": False, "notes": "Massive traffic"},
        {"name": "At-home pet euthanasia", "avg_value": 550, "urgency": 5, "recurring": False, "notes": "Growing"},
        {"name": "Pet hospice care", "avg_value": 1250, "urgency": 4, "recurring": True, "notes": "Aging pets"},
        {"name": "Hot tub repair", "avg_value": 1150, "urgency": 4, "recurring": False, "notes": "Seasonal"},
        {"name": "Pool leak detection", "avg_value": 1250, "urgency": 5, "recurring": False, "notes": "Specialized"},
        {"name": "Sauna installation", "avg_value": 9000, "urgency": 3, "recurring": False, "notes": "Wellness"},
        {"name": "Home automation", "avg_value": 8500, "urgency": 3, "recurring": False, "notes": "Smart home"},
        {"name": "Solar panel installation", "avg_value": 32500, "urgency": 3, "recurring": False, "notes": "Incentives"},
        {"name": "Home battery backup", "avg_value": 20000, "urgency": 3, "recurring": False, "notes": "Solar pairing"},
        {"name": "Soundproofing", "avg_value": 6000, "urgency": 3, "recurring": False, "notes": "Home offices"},
        {"name": "Home theater installation", "avg_value": 55000, "urgency": 2, "recurring": False, "notes": "Luxury"},
        {"name": "Wine cellar construction", "avg_value": 30000, "urgency": 2, "recurring": False, "notes": "Luxury"},
        {"name": "Hurricane shutter installation", "avg_value": 12500, "urgency": 6, "recurring": False, "notes": "Coastal"},
        {"name": "Impact window installation", "avg_value": 30000, "urgency": 5, "recurring": False, "notes": "Hurricane zones"},
        {"name": "Holiday light installation", "avg_value": 2750, "urgency": 4, "recurring": True, "notes": "Seasonal"},
        {"name": "Landscape lighting", "avg_value": 6000, "urgency": 3, "recurring": False, "notes": "Curb appeal"},
        {"name": "Closet organization", "avg_value": 9000, "urgency": 3, "recurring": False, "notes": "Trend"},
        {"name": "Garage organization", "avg_value": 6000, "urgency": 3, "recurring": False, "notes": "Storage"},
        {"name": "Irrigation installation", "avg_value": 6500, "urgency": 3, "recurring": False, "notes": "Lawn"},
        {"name": "Artificial turf", "avg_value": 12500, "urgency": 3, "recurring": False, "notes": "Low maintenance"},
        {"name": "Fence staining", "avg_value": 3000, "urgency": 3, "recurring": True, "notes": "Maintenance"},
        {"name": "Deck staining", "avg_value": 3250, "urgency": 3, "recurring": True, "notes": "Annual"},
        {"name": "Gutter guard installation", "avg_value": 3000, "urgency": 3, "recurring": False, "notes": "Sub-niche"},
        {"name": "Ice dam removal", "avg_value": 1250, "urgency": 7, "recurring": False, "notes": "Winter"},
        {"name": "Lawn aeration", "avg_value": 350, "urgency": 3, "recurring": True, "notes": "Seasonal"},
    ],
    "b2b-services": [
        {"name": "Commercial cleaning", "avg_value": 5500, "urgency": 3, "recurring": True, "notes": "Offices"},
        {"name": "Restaurant hood cleaning", "avg_value": 1250, "urgency": 5, "recurring": True, "notes": "Fire code"},
        {"name": "Commercial HVAC service", "avg_value": 11000, "urgency": 4, "recurring": True, "notes": "Contracts"},
        {"name": "IT support MSP", "avg_value": 6000, "urgency": 4, "recurring": True, "notes": "Recurring"},
        {"name": "Access control installation", "avg_value": 27500, "urgency": 3, "recurring": False, "notes": "Security"},
        {"name": "Security camera installation", "avg_value": 27500, "urgency": 3, "recurring": False, "notes": "Commercial"},
        {"name": "Fire alarm installation", "avg_value": 27500, "urgency": 5, "recurring": False, "notes": "Code"},
        {"name": "Backflow testing", "avg_value": 200, "urgency": 4, "recurring": True, "notes": "Required"},
        {"name": "Elevator maintenance", "avg_value": 6000, "urgency": 4, "recurring": True, "notes": "Contract"},
        {"name": "Document shredding", "avg_value": 1150, "urgency": 3, "recurring": True, "notes": "Compliance"},
        {"name": "Medical billing", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "BPO"},
        {"name": "Vending machine services", "avg_value": 2650, "urgency": 3, "recurring": True, "notes": "Office"},
        {"name": "Fleet washing", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "Contract"},
        {"name": "Commercial snow removal", "avg_value": 11000, "urgency": 4, "recurring": True, "notes": "Seasonal"},
        {"name": "Uniform rental", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "Employee"},
        {"name": "Grease trap cleaning", "avg_value": 650, "urgency": 4, "recurring": True, "notes": "Required"},
        {"name": "Commercial pest control", "avg_value": 2750, "urgency": 4, "recurring": True, "notes": "Food svc"},
        {"name": "Parking lot maintenance", "avg_value": 11000, "urgency": 3, "recurring": True, "notes": "Commercial"},
        {"name": "Records management", "avg_value": 2750, "urgency": 3, "recurring": True, "notes": "Storage"},
        {"name": "Construction cleanup", "avg_value": 11000, "urgency": 4, "recurring": False, "notes": "Post-construction"},
    ],
    "aging-in-place": [
        {"name": "Stairlift installation", "avg_value": 6500, "urgency": 4, "recurring": False, "notes": "Medicare"},
        {"name": "Walk-in tub installation", "avg_value": 10000, "urgency": 4, "recurring": False, "notes": "Accessibility"},
        {"name": "Home elevator", "avg_value": 35000, "urgency": 3, "recurring": False, "notes": "Luxury"},
        {"name": "Wheelchair ramp", "avg_value": 6000, "urgency": 5, "recurring": False, "notes": "ADA"},
        {"name": "Bathroom accessibility remodel", "avg_value": 20000, "urgency": 4, "recurring": False, "notes": "Medicare"},
        {"name": "Tub-to-shower conversion", "avg_value": 10000, "urgency": 4, "recurring": False, "notes": "Aging"},
        {"name": "Walk-in shower", "avg_value": 12500, "urgency": 4, "recurring": False, "notes": "Accessibility"},
        {"name": "Grab bar installation", "avg_value": 500, "urgency": 4, "recurring": False, "notes": "Safety"},
        {"name": "Non-slip flooring", "avg_value": 3000, "urgency": 3, "recurring": False, "notes": "Safety"},
        {"name": "Widening doorways", "avg_value": 2000, "urgency": 4, "recurring": False, "notes": "Accessibility"},
    ],
    "green-eco": [
        {"name": "Solar panel installation", "avg_value": 32500, "urgency": 3, "recurring": False, "notes": "Incentives"},
        {"name": "Home battery backup", "avg_value": 20000, "urgency": 3, "recurring": False, "notes": "Solar pairing"},
        {"name": "EV charger installation", "avg_value": 1750, "urgency": 3, "recurring": False, "notes": "EV growth"},
        {"name": "Whole house water filtration", "avg_value": 6000, "urgency": 3, "recurring": False, "notes": "Health"},
        {"name": "Water softener", "avg_value": 3250, "urgency": 3, "recurring": False, "notes": "Hard water"},
        {"name": "Reverse osmosis", "avg_value": 1250, "urgency": 3, "recurring": False, "notes": "Water quality"},
        {"name": "Energy audit", "avg_value": 550, "urgency": 3, "recurring": False, "notes": "Assessment"},
        {"name": "Insulation upgrade", "avg_value": 4000, "urgency": 3, "recurring": False, "notes": "Efficiency"},
        {"name": "Smart thermostat", "avg_value": 650, "urgency": 3, "recurring": False, "notes": "Smart home"},
        {"name": "LED retrofit", "avg_value": 2000, "urgency": 3, "recurring": False, "notes": "Efficiency"},
    ],
}

# US mid-size cities (50K-500K) — curated for opportunity
# Cities with demographics mismatched to senior services
YOUNG_CITIES = {
    "Aurora IL", "Aurora CO", "Irvine CA", "Plano TX", "Frisco TX", 
    "Gilbert AZ", "Chandler AZ", "Peoria AZ", "Cary NC", "Overland Park KS",
    "Sioux Falls SD", "Provo UT", "Orem UT", "Lehi UT", "Boulder CO",
    "Cambridge MA", "Ann Arbor MI", "Madison WI", "Columbia MO", "College Station TX"
}

# Primarily residential suburbs — weak for B2B services
RESIDENTIAL_SUBURBS = {
    "Blue Mountains NSW", "Blacktown NSW", "Penrith NSW", "Campbelltown NSW",
    "Frankston VIC", "Mornington VIC", "Berwick VIC", "Craigieburn VIC",
    "Gold Coast QLD", "Sunshine Coast QLD", "Mandurah WA", "Albany WA"
}

# Major freight corridors (good for trucking-related niches)
FREIGHT_CORRIDORS = {
    "Penrith NSW", "Wagga Wagga NSW", "Dubbo NSW", "Albury NSW",
    "Wodonga VIC", "Ballarat VIC", "Bendigo VIC", "Shepparton VIC",
    "Toowoomba QLD", "Ipswich QLD", "Geraldton WA", "Kalgoorlie WA"
}

# Small city markets (<50K pop) where B2B demand can be structurally weaker
SMALL_CITIES = {
    "Burnie TAS", "Devonport TAS", "Mount Gambier SA", "Victor Harbor SA",
    "Yass NSW", "Goulburn NSW", "Katherine NT", "Alice Springs NT",
    "Palmerston NT", "Barossa Valley SA", "Albany WA", "Bunbury WA"
}

# Newer-build growth markets with lower foundation repair demand
NEW_CONSTRUCTION_CITIES = {
    "Irvine CA", "Plano TX", "Frisco TX", "Gilbert AZ", "Chandler AZ",
    "Surprise AZ", "West Jordan UT", "Lehigh Acres FL", "League City TX",
    "Sugar Land TX", "Carmel IN"
}

# Retirement destinations (good for senior services)
RETIREMENT_CITIES = {
    "The Villages FL", "Prescott AZ", "Sarasota FL", "Naples FL", 
    "Scottsdale AZ", "St. George UT", "Asheville NC", "Myrtle Beach SC",
    "Venice FL", "Ocala FL", "Port St. Lucie FL", "Cape Coral FL",
    "Hialeah FL", "Miami Gardens FL", "Hollywood FL", "Pembroke Pines FL",
    "Sunrise FL", "Deerfield Beach FL", "Boynton Beach FL", "Delray Beach FL"
}

CITIES = [
    # Suburbs of major metros
    "Fort Worth TX", "Mesa AZ", "Aurora CO", "Arlington TX", "Anaheim CA",
    "Santa Ana CA", "Riverside CA", "Corpus Christi TX", "Lexington KY", "Stockton CA",
    "St. Paul MN", "Toledo OH", "Newark NJ", "Greensboro NC", "Plano TX",
    "Henderson NV", "Lincoln NE", "Buffalo NY", "Jersey City NJ", "Chula Vista CA",
    "Fort Wayne IN", "Orlando FL", "St. Petersburg FL", "Chandler AZ", "Laredo TX",
    "Madison WI", "Durham NC", "Lubbock TX", "Winston-Salem NC", "Garland TX",
    "Glendale AZ", "Hialeah FL", "Reno NV", "Chesapeake VA", "Scottsdale AZ",
    "North Las Vegas NV", "Irving TX", "Fremont CA", "Irvine CA", "Birmingham AL",
    "Rochester NY", "San Bernardino CA", "Spokane WA", "Gilbert AZ", "Montgomery AL",
    "Boise ID", "Fayetteville NC", "Richmond VA", "Des Moines IA", "Modesto CA",
    "Shreveport LA", "Tacoma WA", "Oxnard CA", "Aurora IL", "Moreno Valley CA",
    "Fontana CA", "Yonkers NY", "Augusta GA", "Mobile AL", "Little Rock AR",
    "Amarillo TX", "Huntington Beach CA", "Grand Rapids MI", "Salt Lake City UT",
    "Tallahassee FL", "Huntsville AL", "Worcester MA", "Knoxville TN", "Providence RI",
    "Newport News VA", "Brownsville TX", "Cape Coral FL", "Ontario CA", "Sioux Falls SD",
    "Chattanooga TN", "Fort Lauderdale FL", "Springfield MO", "Pembroke Pines FL",
    "Vancouver WA", "Jackson MS", "Santa Rosa CA", "Springfield MA", "Kansas City KS",
    "Sunnyvale CA", "Pomona CA", "Hollywood FL", "Pasadena TX", "Escondido CA",
    "Naperville IL", "Joliet IL", "Syracuse NY", "Mesquite TX", "Torrance CA",
    "Dayton OH", "Savannah GA", "Clarksville TN", "Orange CA", "Pasadena CA",
    "Fullerton CA", "Killeen TX", "Frisco TX", "Hampton VA", "McAllen TX",
    "Warren MI", "Bellevue WA", "West Valley City UT", "Columbia SC", "Olathe KS",
    "Sterling Heights MI", "New Haven CT", "Miramar FL", "Waco TX", "Thousand Oaks CA",
    "Cedar Rapids IA", "Charleston SC", "Visalia CA", "Topeka KS", "Elizabeth NJ",
    "Gainesville FL", "Carrollton TX", "Coral Springs FL", "Stamford CT", "Hartford CT",
    "Concord CA", "Roseville CA", "Thornton CO", "Kent WA", "Lafayette LA",
    "Surprise AZ", "Denton TX", "Victorville CA", "Evansville IN", "Midland TX",
    "Athens GA", "Allentown PA", "Abilene TX", "Beaumont TX", "Vallejo CA",
    "Provo UT", "Murfreesboro TN", "Ann Arbor MI", "Berkeley CA", "Peoria IL",
    "Lansing MI", "El Monte CA", "Independence MO", "Downey CA", "Costa Mesa CA",
    "Inglewood CA", "Miami Gardens FL", "Manchester NH", "Wilmington NC", "Westminster CO",
    "Gresham OR", "Clearwater FL", "Lowell MA", "West Jordan UT", "Pueblo CO",
    "San Buenaventura CA", "Fairfield CA", "West Covina CA", "Billings MT", "Murrieta CA",
    "Norwalk CA", "Elgin IL", "Palm Bay FL", "Columbia MO", "Everett WA",
    "El Cajon CA", "Temecula CA", "Burbank CA", "Richardson TX", "Broken Arrow OK",
    "West Palm Beach FL", "Lehigh Acres FL", "Manchester CT", "Boulder CO", "Rialto CA",
    "Daly City CA", "Sandy Springs GA", "Green Bay WI", "Norwalk CT", "Lewisville TX",
    "Hillsboro OR", "Albany NY", "Tyler TX", "Las Cruces NM", "Cambridge MA",
    "League City TX", "Brockton MA", "Roanoke VA", "Portsmouth VA", "Yuma AZ",
    "Sandy UT", "Sparks NV", "Sugar Land TX", "Federal Way WA", "San Mateo CA",
    "Nampa ID", "Edinburg TX", "Redwood City CA", "Bloomington MN", "Suffolk VA",
    "Mission TX", "Quincy MA", "New Bedford MA", "Boca Raton FL", "Carmel IN",
    # Australian cities (for Okeito)
    "Geelong VIC", "Ballarat VIC", "Bendigo VIC", "Shepparton VIC", "Wollongong NSW",
    "Newcastle NSW", "Central Coast NSW", "Blue Mountains NSW", "Gold Coast QLD",
    "Sunshine Coast QLD", "Toowoomba QLD", "Ipswich QLD", "Mandurah WA",
    "Bunbury WA", "Geraldton WA", "Albany WA", "Mount Gambier SA",
    "Victor Harbor SA", "Gawler SA", "Barossa Valley SA", "Queanbeyan NSW",
    "Yass NSW", "Goulburn NSW", "Launceston TAS", "Devonport TAS", "Burnie TAS",
    "Palmerston NT", "Katherine NT", "Alice Springs NT",
]

def calculate_opportunity_score(niche, city, estimated_leads=50, seo_metrics=None):
    """Calculate opportunity score using weighted market-fit scoring.

    Weights:
    - Lead Value: 2.0x
    - Low Competition: 2.5x (inverted KD)
    - Traffic: 1.5x
    - Urgency: 1.5x
    """
    avg_value = niche["avg_value"]
    urgency = niche["urgency"]

    # Lead value calculation (Kyle's formula simplified)
    # Assume 30% close rate, 3 leads per job
    lead_value = (avg_value * 0.30) / 3

    # Adjust estimated leads based on job value (higher ticket = fewer leads)
    if avg_value > 20000:
        estimated_leads = 10  # High ticket, low volume
    elif avg_value > 10000:
        estimated_leads = 20  # Medium-high ticket
    elif avg_value > 5000:
        estimated_leads = 35  # Medium ticket
    else:
        estimated_leads = 50  # Low ticket, high volume

    monthly_fee = lead_value * estimated_leads * 0.4  # 40% of value

    # Cap monthly fee at realistic R&R range
    monthly_fee = max(300, min(monthly_fee, 2500))

    # Lead Value Score: $20K = 10, $2K = 1 (capped)
    lead_value_score = min(10, avg_value / 2000)

    # Location-Industry Fit Penalty
    location_fit = 1.0
    niche_name_lower = niche["name"].lower()
    city_lower = city.lower()

    # B2B in small cities or residential suburbs = weak fit
    b2b_keywords = [
        "cybersecurity", "fractional cfo", "msp", "commercial cleaning", "commercial pest",
        "business coaching", "payroll", "bookkeeping", "it support", "records management",
        "fleet washing", "commercial", "industrial", "b2b"
    ]
    if any(x in niche_name_lower for x in b2b_keywords) or niche.get("b2b", False):
        # Check if city is small (<50K pop) or residential suburb
        small_cities = [
            "palmerston", "lewisville", "frankston", "mornington", "berwick", "craigieburn",
            "mandurah", "albany", "gawler", "victor harbor", "bunbury", "geraldton",
            "kalgoorlie", "toowoomba", "ipswich", "shepparton", "wodonga", "warrnambool"
        ]
        if any(x in city_lower for x in small_cities) or city in RESIDENTIAL_SUBURBS:
            location_fit = 0.4
            penalty_reason = "B2B niche in small city or residential suburb"
        elif any(x in city_lower for x in ["dallas", "houston", "chicago", "new york", "los angeles", "san francisco", "boston", "seattle", "denver", "atlanta", "austin", "phoenix", "miami"]):
            location_fit = 1.2
            penalty_reason = "B2B niche in major metro business district"
    
    # Trucking attorney needs freight corridors
    if any(word in niche_name_lower for word in ["trucking", "truck"]):
        if any(x in city_lower for x in ["mountain", "blue mountains", "coast", "beach", "village"]):
            location_fit = 0.2
        elif not any(x in city_lower for x in ["wagga", "dubbo", "albury", "ballarat", "bendigo", "toowoomba", "ipswich", "geraldton", "kalgoorlie"]):
            location_fit = 0.5
    
    # Senior services need retirement cities
    if any(x in niche_name_lower for x in ["walk-in tub", "stairlift", "senior", "aging", "accessibility", "walk-in shower", "bathroom accessibility"]):
        if any(x in city_lower for x in ["aurora il", "denton tx", "irvine", "plano", "frisco", "gilbert", "chandler", "madison", "columbia", "college station"]):
            location_fit = 0.3
        elif any(x in city_lower for x in ["hialeah", "naples", "sarasota", "prescott", "the villages", "st. george", "myrtle beach", "venice", "ocala", "port st. lucie", "cape coral"]):
            location_fit = 1.2
    
    # Foundation repair needs older housing
    if "foundation" in niche_name_lower:
        if any(x in city_lower for x in ["irvine", "plano", "frisco", "gilbert", "chandler", "new"]):
            location_fit = 0.6
    
    # Water damage needs flood-prone areas
    if any(x in niche_name_lower for x in ["water damage", "storm damage", "flood"]):
        if any(x in city_lower for x in ["desert", "phoenix", "tucson", "vegas"]):
            location_fit = 0.4
    
    # Home battery backup needs solar-friendly cities
    if "home battery" in niche_name_lower or "battery backup" in niche_name_lower:
        if any(x in city_lower for x in ["seattle", "portland", "chicago", "detroit", "minneapolis"]):
            location_fit = 0.5
    
    # Backflow testing, grease trap, energy audit = near-zero search volume, compliance-driven
    if any(x in niche_name_lower for x in ["backflow testing", "backflow inspection", "grease trap", "energy audit", "energy assessment"]):
        location_fit = 0.2
        penalty_reason = "Compliance-driven market, not search-driven"
    
    # Smart thermostat = DIY dominates, oversaturated
    if any(x in niche_name_lower for x in ["smart thermostat", "thermostat installation"]):
        location_fit = 0.3
        penalty_reason = "DIY dominates, HVAC upsell, not standalone"
    
    # At-home pet euthanasia = crisis = call vet, not Google
    if any(x in niche_name_lower for x in ["at-home pet euthanasia", "home pet euthanasia"]):
        location_fit = 0.3
        penalty_reason = "Crisis moment = call vet, not Google search"
    
    # Home battery backup needs solar-friendly cities (not just any city)
    if "home battery" in niche_name_lower or "battery backup" in niche_name_lower:
        if any(x in city_lower for x in ["seattle", "portland", "chicago", "detroit", "minneapolis", "boston", "new york"]):
            location_fit = 0.3
            penalty_reason = "Low solar adoption city"
        elif any(x in city_lower for x in ["phoenix", "tucson", "las vegas", "austin", "san diego", "los angeles", "miami", "tampa", "orlando", "denver", "salt lake"]):
            location_fit = 1.2
            penalty_reason = "High solar adoption city"
    
    # Solar panel installation needs solar-friendly climate
    if "solar panel" in niche_name_lower or "solar installation" in niche_name_lower:
        if any(x in city_lower for x in ["seattle", "portland", "chicago", "detroit", "minneapolis", "boston", "new york", "cleveland", "pittsburgh"]):
            location_fit = 0.5
            penalty_reason = "Low solar irradiance, poor ROI"
        elif any(x in city_lower for x in ["phoenix", "tucson", "las vegas", "austin", "san diego", "los angeles", "miami", "tampa", "orlando", "denver", "salt lake", "fresno", "bakersfield", "riverside", "stockton", "modesto", "visalia", "merced"]):
            location_fit = 1.2
            penalty_reason = "High solar irradiance, strong incentives"
    
    # Lawn aeration = seasonal upsell, not standalone
    if any(x in niche_name_lower for x in ["lawn aeration", "lawn aerating", "core aeration"]):
        location_fit = 0.3
        penalty_reason = "Seasonal upsell, every lawn company offers this"
    
    # Hot tub repair = seasonal, bundled with pool services
    if any(x in niche_name_lower for x in ["hot tub repair", "hot tub service", "spa repair"]):
        location_fit = 0.4
        penalty_reason = "Seasonal, bundled with pool services"
    
    # Grab bar installation = low ticket, remodel add-on
    if any(x in niche_name_lower for x in ["grab bar installation", "grab bar install", "shower grab bar"]):
        location_fit = 0.4
        penalty_reason = "Low ticket, usually bundled with larger remodel"
    
    # Home elevator = tiny market, massive liability
    if any(x in niche_name_lower for x in ["home elevator", "residential elevator", "house elevator"]):
        location_fit = 0.3
        penalty_reason = "Tiny market, 6-12 month sales cycle, high liability"
    
    # LED retrofit = B2B relationship-driven
    if any(x in niche_name_lower for x in ["led retrofit", "led lighting retrofit", "commercial led"]):
        location_fit = 0.5
        penalty_reason = "B2B relationship-driven, not search-driven"
    
    # Competition Score: KD 10 = 10, KD 50 = 6 (inverted — lower is better)
    kd = seo_metrics.get("keyword_difficulty", 25) if seo_metrics else 25
    competition_score = max(0, 11 - (kd / 10))
    
    # Traffic Score: 150 searches = 10, 30 = 2
    search_volume = seo_metrics.get("search_volume", 50) if seo_metrics else 50
    traffic_score = min(10, search_volume / 15)
    
    # Urgency Score: 10 = 1.0, 5 = 0.5
    urgency_score = urgency / 10
    
    # REVISED Kyle weights (less dominated by job value):
    # Lead Value (1.5x) + Low Competition (2.5x) + Traffic (2.0x) + Urgency (1.5x)
    # Competition and traffic matter MORE than extreme job values
    composite_score = (
        (lead_value_score * 1.5) +
        (competition_score * 2.5) +
        (traffic_score * 2.0) +
        (urgency_score * 1.5)
    ) * location_fit  # Apply location fit penalty/boost
    
    # Normalize to 0-100 scale and round
    opportunity_score = min(100, max(0, round(composite_score * 1.8, 1)))
    
    # Priority classification based on score
    if opportunity_score >= 75:
        priority = "Start Now"
    elif opportunity_score >= 55:
        priority = "Research Further"
    elif opportunity_score >= 35:
        priority = "Monitor"
    else:
        priority = "Low Priority"
    
    return {
        "monthly_fee": round(monthly_fee, 0),
        "lead_value": round(lead_value, 0),
        "opportunity_score": opportunity_score,
        "estimated_leads": estimated_leads,
        "priority": priority,
        "location_fit": location_fit,
        "kyle_breakdown": {
            "lead_value_score": round(lead_value_score, 1),
            "competition_score": round(competition_score, 1),
            "traffic_score": round(traffic_score, 1),
            "urgency_score": round(urgency_score, 1),
            "location_fit": location_fit,
            "composite_raw": round(composite_score, 1)
        }
    }


def generate_web_prompt(niche_name, city_name, avg_value, urgency, recurring, domain, monthly_fee, seo_metrics):
    """Generate a detailed web development prompt for an AI developer."""
    
    # Determine page structure based on niche type
    if "attorney" in niche_name.lower() or "lawyer" in niche_name.lower():
        page_type = "legal_service"
        cta_primary = "Free Consultation"
        cta_secondary = "Case Evaluation"
        trust_elements = "Bar association badges, client testimonials, case results, AVVO rating"
    elif any(word in niche_name.lower() for word in ["emergency", "damage", "repair", "cleanup", "removal"]):
        page_type = "emergency_service"
        cta_primary = "Call Now for Immediate Help"
        cta_secondary = "Get a Free Quote"
        trust_elements = "24/7 availability badge, response time guarantee, before/after photos, insurance accepted"
    elif any(word in niche_name.lower() for word in ["installation", "construction", "remodel", "renovation"]):
        page_type = "installation_service"
        cta_primary = "Free Estimate"
        cta_secondary = "Schedule Consultation"
        trust_elements = "Portfolio gallery, manufacturer certifications, warranty info, financing available"
    else:
        page_type = "professional_service"
        cta_primary = "Free Consultation"
        cta_secondary = "Get Started"
        trust_elements = "Credentials, testimonials, process explanation, FAQ section"
    
    recurring_note = "This is a recurring service — include a subscription/membership CTA option." if recurring else ""
    
    prompt = f"""# Lead Generation Website Build — {niche_name} in {city_name}

## Overview
Build a high-converting, mobile-first lead generation website for **{niche_name}** targeting **{city_name}**. This is a Rank & Rent site designed to capture leads and forward them to a local service provider for a monthly fee of **${monthly_fee:,.0f}**.

## Target Market
- **Location:** {city_name}
- **Service:** {niche_name}
- **Average Job Value:** ${avg_value:,}
- **Urgency Level:** {urgency}/10 ({('Emergency — immediate response needed' if urgency >= 8 else 'High priority — same day response' if urgency >= 6 else 'Standard — 24-48hr response')})
- **Page Type:** {page_type}

## Primary Keywords to Target
- Main: "{niche_name} {city_name}"
- Secondary: "best {niche_name} near me", "{niche_name} company {city_name}", "affordable {niche_name} {city_name}"
- Long-tail: "{niche_name} cost {city_name}", "{niche_name} reviews {city_name}", "how much does {niche_name} cost in {city_name}"

## Domain
**Primary:** {domain}
(Verify availability before building)

## Page Structure
### Required Pages
1. **Homepage** — Hero + trust signals + service overview + CTA + FAQ
2. **Services** — Detailed service page with pricing context
3. **About** — Company story, credentials, service area
4. **Contact** — Form + phone + map + hours
5. **Areas We Serve** — List of suburbs/neighborhoods in {city_name}
6. **Blog** — 3-5 seed articles targeting long-tail keywords

### Homepage Sections (Top to Bottom)
1. **Sticky Header** — Logo + Phone number (click-to-call) + CTA button
2. **Hero Section** — H1: "{niche_name} in {city_name}" + subheadline with benefit + 2 CTAs ({cta_primary} / {cta_secondary})
3. **Trust Bar** — 3 trust badges (e.g., "Licensed & Insured", "Same Day Service", "Free Estimates")
4. **Services Grid** — 3-6 service cards with icons
5. **Why Choose Us** — 3-4 differentiators with icons
6. **Social Proof** — Testimonials (use realistic placeholder names/cities)
7. **FAQ Accordion** — 5-7 common questions (great for SEO + voice search)
8. **CTA Banner** — Secondary conversion push
9. **Footer** — Full nav + contact + service areas + social links

## Design Requirements
- **Style:** Clean, professional, high-trust. Avoid templates.
- **Colors:** Blue + white + orange accents (proven conversion colors)
- **Typography:** Sans-serif, large readable text, clear hierarchy
- **Mobile:** 70%+ traffic will be mobile — optimize for thumbs, click-to-call prominent
- **Speed:** Target <2s load time. Optimize images, minify CSS/JS
- **Accessibility:** WCAG 2.1 AA compliant

## Conversion Optimization
- **Above the fold:** Phone number + form visible without scrolling
- **Click-to-call:** Every phone number is a tap-to-call link
- **Form:** Name + Phone + Service Needed + Address (4 fields max)
- **Trust signals:** {trust_elements}
- **Urgency:** {('24/7 Emergency Service' if urgency >= 8 else 'Same Day Appointments Available')}
- **Social proof:** 3+ testimonials with photos, star ratings
- **Risk reversal:** "Free Quote", "No Obligation", "Satisfaction Guaranteed"

## SEO Requirements
- **Meta:** Unique title + description for every page
- **Schema:** LocalBusiness structured data with {city_name} address
- **H1:** Exactly "{niche_name} {city_name}" on homepage
- **Internal linking:** Every page links to contact page
- **Image alt text:** Descriptive, keyword-rich
- **URL structure:** /{niche_name.lower().replace(' ', '-')}-{city_name.lower().replace(' ', '-')}/
- **Local content:** Mention specific neighborhoods, landmarks, weather/seasonal context for {city_name}
- **FAQ Schema:** Mark up FAQ section for rich snippets

## Technical Stack
- **Static HTML/CSS/JS** (no CMS needed for lead gen)
- **Form handling:** Use Formspree, Basin, or similar (forward to email)
- **Analytics:** Google Analytics 4 + Google Search Console
- **Hosting:** Netlify, Vercel, or Cloudflare Pages (free SSL + CDN)
- **Domain:** Connect to {domain} via DNS

## Lead Forwarding Setup
- Form submissions → Email to [your email]
- Phone number → Forward to [client's phone] via Google Voice or similar
- Set up tracking: Use unique phone number per site to measure call volume

## Content Guidelines
- **Tone:** Professional but approachable
- **Length:** 800-1200 words on homepage, 500+ on service pages
- **FAQ Questions:**
  1. "How much does {niche_name} cost in {city_name}?"
  2. "How long does {niche_name} take?"
  3. "Do you offer free estimates?"
  4. "Are you licensed and insured?"
  5. "What areas do you serve?"
  6. "Do you offer emergency {niche_name}?"
  7. "What payment options do you accept?"

## Deliverables
1. Complete static website (HTML/CSS/JS)
2. Responsive design (mobile-first)
3. Contact form with validation
4. Google Analytics installed
5. Search Console submitted
6. LocalBusiness schema markup
7. 5 blog article drafts (300-500 words each)
8. README with deployment instructions

## Success Metrics
- **Target:** First lead within 30 days of going live
- **Goal:** 5+ leads/month within 90 days
- **Monthly Fee:** ${monthly_fee:,.0f}/month from client

{recurring_note}

---
**Budget Estimate:** $200-500 for initial build (one-time)
**Monthly Maintenance:** $50-100 (content updates, monitoring)
"""
    return prompt


def generate_domain_suggestion(niche_name, city_name):
    """Generate domain name suggestions"""
    niche_clean = niche_name.lower().replace(" ", "").replace("-", "")
    city_clean = city_name.lower().replace(" ", "").replace(",", "").replace(".", "")
    
    suggestions = [
        f"{niche_clean}{city_clean}.com",
        f"{city_clean}{niche_clean}.com",
        f"{niche_clean}-{city_clean}.com",
        f"{city_clean}-{niche_clean}.com",
        f"best{niche_clean}{city_clean}.com",
        f"{niche_clean}pro{city_clean}.com",
    ]
    return suggestions[:3]

def get_city_profile(city_name):
    """Rough city profile for location reasoning."""
    lower_city = city_name.lower()

    large_markets = ["fort worth", "orlando", "salt lake city", "newcastle", "gold coast"]
    smaller_markets = ["burnie", "albany", "yass", "gawler", "katherine", "victor harbor"]

    if any(name in lower_city for name in large_markets):
        population_band = "Upper mid-size market (~250K-500K)"
        city_trait = "high service demand with enough population density for lead volume"
    elif any(name in lower_city for name in smaller_markets):
        population_band = "Smaller mid-size market (~50K-150K)"
        city_trait = "tight local market where weak incumbents are easier to outrank"
    else:
        population_band = "Mid-size market (~100K-350K)"
        city_trait = "balanced demand without major-metro SEO saturation"

    return {
        "population_band": population_band,
        "city_trait": city_trait,
    }


def generate_location_reasoning(niche_name, city_name, seo_metrics):
    """Generate SEO-driven explanation for why this city was selected."""
    profile = get_city_profile(city_name)
    competition = seo_metrics.get("competition_level", "Medium")
    competitor_da = seo_metrics.get("competitor_da", "N/A")
    map_pack = seo_metrics.get("map_pack_status", "Unknown")

    return (
        f"{city_name} sits in the {profile['population_band']} where rank-and-rent performs best. "
        f"Current market signal is {competition.lower()} competition (top competitor DA ~{competitor_da}, map pack: {map_pack}), "
        f"which indicates an underserved or weak-incumbent opening for {niche_name.lower()} leads. "
        f"City fit: {profile['city_trait']}."
    )


def generate_urgency_reason(niche_name, urgency_score):
    """Generate niche-specific urgency rationale."""
    niche_lower = niche_name.lower()
    if urgency_score >= 8:
        if any(word in niche_lower for word in ["damage", "pipe", "backup", "cleanup", "remediation", "repair"]):
            return "Emergency services score high (8-10): customers need immediate help, often same-hour or same-day."
        return "High urgency (8-10): this niche is usually triggered by urgent, high-stress incidents."
    if urgency_score >= 5:
        return "Moderate-high urgency (5-7): buyers typically want same-day to next-day response."
    return "Lower urgency (1-4): demand is planned/considered, so response speed matters less than trust and pricing."


def find_opportunities(category=None, count=5, include_australian=False):
    """Find top opportunities"""
    opportunities = []
    
    # Select niches
    if category and category in NICHE_DATABASE:
        niches = NICHE_DATABASE[category]
    else:
        # Mix from all categories
        niches = []
        for cat, items in NICHE_DATABASE.items():
            niches.extend(items)
    
    # Select cities
    cities = CITIES.copy()
    if not include_australian:
        cities = [c for c in cities if not any(state in c for state in ["VIC", "NSW", "QLD", "WA", "SA", "TAS", "NT"])]
    
    # Generate random combos
    random.shuffle(niches)
    random.shuffle(cities)
    
    for i in range(min(count, len(niches))):
        niche = niches[i]
        city = cities[i % len(cities)]
        
        # Skip niches that are known time-wasters (compliance-driven, DIY-dominated, etc.)
        skip_niches = [
            "backflow testing", "backflow inspection", "grease trap", "grease trap cleaning",
            "energy audit", "energy assessment", "smart thermostat", "thermostat installation",
            "at-home pet euthanasia", "home pet euthanasia", "lawn aeration", "lawn aerating",
            "core aeration", "hot tub repair", "hot tub service", "spa repair",
            "grab bar installation", "grab bar install", "shower grab bar",
            "home elevator", "residential elevator", "house elevator",
            "led retrofit", "led lighting retrofit", "commercial led"
        ]
        if any(x in niche["name"].lower() for x in skip_niches):
            continue
        
        # Add SEO metrics (estimated based on niche characteristics)
        # In production, these would come from Ahrefs/Mangools API
        seo_metrics = calculate_seo_metrics(niche, city)
        
        # Calculate opportunity score with SEO metrics (enhanced Kyle framework)
        calc = calculate_opportunity_score(niche, city=city, seo_metrics=seo_metrics)
        if calc is None:
            continue
        
        # Skip low-priority opportunities (score < 50)
        if calc["opportunity_score"] < 50:
            continue
        
        domains = generate_domain_suggestion(niche["name"], city)
        
        # Generate web development prompt
        web_prompt = generate_web_prompt(
            niche_name=niche["name"],
            city_name=city,
            avg_value=niche["avg_value"],
            urgency=niche["urgency"],
            recurring=niche["recurring"],
            domain=domains[0],
            monthly_fee=calc["monthly_fee"],
            seo_metrics=seo_metrics
        )
        
        urgency_reason = generate_urgency_reason(niche["name"], niche["urgency"])
        location_reasoning = generate_location_reasoning(niche["name"], city, seo_metrics)

        opportunities.append({
            "niche": niche["name"],
            "city": city,
            "avg_job_value": niche["avg_value"],
            "monthly_fee": calc["monthly_fee"],
            "lead_value": calc["lead_value"],
            "opportunity_score": calc["opportunity_score"],
            "urgency": niche["urgency"],
            "urgency_reason": urgency_reason,
            "recurring": niche["recurring"],
            "domain_suggestions": domains,
            "location_reasoning": location_reasoning,
            "priority": calc.get("priority", "Monitor"),
            "status": "New",
            "notes": niche["notes"],
            "action_plan": [
                f"1. Search Google for '{niche['name']} {city}' — verify competition",
                f"2. Check domain availability: {domains[0]}",
                f"3. If green light: build site + get ranking"
            ],
            "seo": seo_metrics,
            "web_prompt": web_prompt
        })
    
    # Sort by opportunity score
    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
    return opportunities

def format_opportunities(opportunities):
    """Format as markdown report"""
    lines = []
    lines.append("# Rank & Rent Opportunity Batch")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Opportunities Found:** {len(opportunities)}")
    lines.append("")
    lines.append("## Summary Table")
    lines.append("")
    lines.append("| Rank | Niche | City | Monthly Fee | Score | Priority |")
    lines.append("|------|-------|------|-------------|-------|----------|")
    
    for i, opp in enumerate(opportunities, 1):
        lines.append(f"| {i} | {opp['niche']} | {opp['city']} | ${opp['monthly_fee']:.0f} | {opp['opportunity_score']} | {opp['priority']} |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Detailed Opportunity Cards")
    lines.append("")
    
    for i, opp in enumerate(opportunities, 1):
        lines.append(f"### #{i}: {opp['niche']} in {opp['city']}")
        lines.append("")
        lines.append(f"- **Average Job Value:** ${opp['avg_job_value']:,}")
        lines.append(f"- **Estimated Lead Value:** ${opp['lead_value']:.0f}")
        lines.append(f"- **Recommended Monthly Fee:** ${opp['monthly_fee']:.0f}")
        lines.append(f"- **Urgency Level:** {opp['urgency']}/10")
        lines.append(f"- **Urgency Reason:** {opp.get('urgency_reason', '')}")
        lines.append(f"- **Recurring Potential:** {'Yes' if opp['recurring'] else 'No'}")
        lines.append(f"- **Opportunity Score:** {opp['opportunity_score']}/10")
        lines.append(f"- **Priority:** {opp['priority']}")
        lines.append(f"- **Status:** {opp.get('status', 'New')}")
        lines.append(f"- **Notes:** {opp['notes']}")
        lines.append(f"- **Location Reasoning:** {opp.get('location_reasoning', '')}")
        lines.append("")
        lines.append("**SEO Metrics (Estimated):**")
        seo = opp.get('seo', {})
        lines.append(f"- **Search Volume:** {seo.get('search_volume', 'N/A')} searches/month")
        lines.append(f"- **Keyword Difficulty:** {seo.get('keyword_difficulty', 'N/A')}/100")
        lines.append(f"- **Competition Level:** {seo.get('competition_level', 'N/A')}")
        lines.append(f"- **Backlink Estimate:** {seo.get('backlink_estimate', 'N/A')}")
        lines.append(f"- **Map Pack Status:** {seo.get('map_pack_status', 'N/A')}")
        lines.append(f"- **Top Competitor DA:** {seo.get('competitor_da', 'N/A')}")
        lines.append(f"- **Content Gap Score:** {seo.get('content_gap_score', 'N/A')}/100")
        lines.append(f"- **SEO Opportunity Score:** {seo.get('seo_opportunity_score', 'N/A')}/100")
        lines.append(f"- **Status:** {'⚠️ Estimated — verify with Ahrefs/Mangools' if seo.get('verification_needed') else '✅ Verified'}")
        lines.append("")
        lines.append("**Domain Suggestions:**")
        for domain in opp['domain_suggestions']:
            lines.append(f"- `{domain}`")
        lines.append("")
        lines.append("**Action Plan:**")
        for step in opp['action_plan']:
            lines.append(f"- {step}")
        lines.append("")
        # Embed web prompt as hidden HTML comment for extraction
        lines.append(f"<!--WEB_PROMPT-->")
        lines.append(f"{opp.get('web_prompt', '')}")
        lines.append(f"<!--/WEB_PROMPT-->")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Find rank and rent niche opportunities")
    parser.add_argument("--category", help="Niche category to focus on")
    parser.add_argument("--count", type=int, default=5, help="Number of opportunities to generate")
    parser.add_argument("--australian", action="store_true", help="Include Australian cities")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()
    
    print(f"🔍 Searching for {args.count} opportunities...", file=sys.stderr)
    
    opportunities = find_opportunities(
        category=args.category,
        count=args.count,
        include_australian=args.australian
    )
    
    report = format_opportunities(opportunities)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to: {args.output}", file=sys.stderr)
    else:
        print(report)
    
    return opportunities

if __name__ == "__main__":
    main()
