"""
generators/hospital_gen.py
Generate realistic Indian hospital profiles with regional naming,
Rohini IDs, city tiers, and phantom hospital injection.
"""

import numpy as np
import pandas as pd

from config import (
    CITY_TIER_WEIGHTS,
    PHANTOM_HOSPITAL_RATE,
    HOSPITAL_SPECIALIZATIONS,
    SPECIALIZATION_WEIGHTS_TIER1,
    SPECIALIZATION_WEIGHTS_TIER2,
    SPECIALIZATION_WEIGHTS_TIER3,
    CLAIM_START_DATE,
    RANDOM_SEED,
)

# ─── City Pools by Tier ──────────────────────────────────────────────────────
CITIES = {
    "tier1": [
        ("Mumbai", "west"), ("Delhi", "hindi_belt"), ("Bengaluru", "south"),
        ("Chennai", "south"), ("Hyderabad", "south"), ("Kolkata", "east"),
        ("Pune", "west"), ("Ahmedabad", "west"),
    ],
    "tier2": [
        ("Lucknow", "hindi_belt"), ("Jaipur", "hindi_belt"),
        ("Chandigarh", "hindi_belt"), ("Nagpur", "west"),
        ("Indore", "hindi_belt"), ("Bhopal", "hindi_belt"),
        ("Coimbatore", "south"), ("Visakhapatnam", "south"),
        ("Kochi", "south"), ("Madurai", "south"),
        ("Vadodara", "west"), ("Patna", "hindi_belt"),
        ("Thiruvananthapuram", "south"), ("Ludhiana", "hindi_belt"),
    ],
    "tier3": [
        ("Varanasi", "hindi_belt"), ("Allahabad", "hindi_belt"),
        ("Jodhpur", "hindi_belt"), ("Amritsar", "hindi_belt"),
        ("Ranchi", "hindi_belt"), ("Dehradun", "hindi_belt"),
        ("Tiruchirappalli", "south"), ("Salem", "south"),
        ("Vellore", "south"), ("Guntur", "south"),
        ("Rajkot", "west"), ("Bhavnagar", "west"),
        ("Siliguri", "east"), ("Durgapur", "east"),
    ],
}

# ─── Hospital Name Templates by Region ───────────────────────────────────────
HOSPITAL_TEMPLATES = {
    "hindi_belt": [
        "{deity} अस्पताल", "श्री {surname} मेडिकल सेंटर",
        "{city} जिला अस्पताल", "Shri {surname} Medical Centre",
        "{deity} Care Hospital", "आयुष्मान {surname} क्लिनिक",
        "{surname} Hospital & Research Centre", "{city} City Hospital",
    ],
    "south": [
        "{deity} Hospital and Research Centre",
        "Sri {surname} Multi-Speciality Hospital",
        "காந்தி மருத்துவமனை", "Vijaya {surname} Hospital",
        "ஸ்ரீ {deity} கிளினிக்", "{surname} Apollo Clinic",
        "{city} Medical Centre", "Sri {surname} Nursing Home",
    ],
    "west": [
        "{surname} Hospital Pvt Ltd", "Shree {deity} Multispeciality",
        "સર {surname} હૉસ્પિટલ", "{city} Nursing Home",
        "Wockhardt {city} Centre", "{surname} Medical Foundation",
        "{deity} Healthcare {city}", "Shree {surname} Clinic",
    ],
    "east": [
        "{surname} Nursing Home", "Calcutta {deity} Hospital",
        "সেবা নার্সিং হোম", "{surname} Medical College & Hospital",
        "{city} General Hospital", "Sri {deity} Institute",
        "{surname} Seva Sadan", "Eastern {surname} Hospital",
    ],
    "phantom": [
        "{city} Advanced Wellness Hub", "National {deity} Diagnostic Centre",
        "IndiaFirst HealthCare {city}", "MedPro Solutions {city}",
        "QuickHeal Clinic {city}", "Global {city} Wellness",
        "Prime Medicare {city}", "SuperCare Diagnostics {city}",
    ],
}

# Template fill data
DEITIES = [
    "Ram", "Krishna", "Ganesh", "Shiv", "Durga", "Lakshmi",
    "Hanuman", "Vishnu", "Saraswati", "Venkateswara",
]
SURNAMES = [
    "Agarwal", "Gupta", "Patel", "Reddy", "Sharma", "Iyer",
    "Mehta", "Choudhary", "Naidu", "Pillai", "Joshi", "Kapoor",
    "Rao", "Desai", "Banerjee", "Das", "Nair", "Menon",
]


def _generate_rohini_id(is_phantom: bool, rng: np.random.Generator) -> str:
    """Generate Rohini ID. Valid format: ROHINI-[1-8][0-9]{5} for real hospitals."""
    if is_phantom:
        # Invalid formats for phantom hospitals
        bad_formats = [
            f"ROH-{rng.integers(10000, 99999)}",
            f"ROHINI-0{rng.integers(10000, 99999)}",  # starts with 0
            f"ROHINI-9{rng.integers(10000, 99999)}",  # starts with 9
            "",
            "PENDING",
            "NA",
        ]
        return rng.choice(bad_formats)
    else:
        first = rng.integers(1, 9)  # 1-8
        rest = rng.integers(10000, 99999)
        return f"ROHINI-{first}{rest}"


def _generate_hospital_name(region: str, city: str, rng: np.random.Generator) -> str:
    """Generate a hospital name from regional templates."""
    templates = HOSPITAL_TEMPLATES.get(region, HOSPITAL_TEMPLATES["hindi_belt"])
    template = rng.choice(templates)
    deity = rng.choice(DEITIES)
    surname = rng.choice(SURNAMES)
    return template.format(deity=deity, surname=surname, city=city)


def generate_hospitals(n_hospitals: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate n_hospitals Indian hospital profiles."""
    records = []

    for i in range(n_hospitals):
        hospital_id = f"H{i+1:04d}"

        # Is phantom?
        is_phantom = rng.random() < PHANTOM_HOSPITAL_RATE

        # Pick tier
        tier_idx = rng.choice([0, 1, 2], p=CITY_TIER_WEIGHTS)
        tier = tier_idx + 1
        tier_key = f"tier{tier}"

        # Pick city and region
        city, region = CITIES[tier_key][rng.integers(0, len(CITIES[tier_key]))]

        # Override region for phantom hospitals
        name_region = "phantom" if is_phantom else region

        # Generate name
        name = _generate_hospital_name(name_region, city, rng)

        # Rohini ID
        rohini_id = _generate_rohini_id(is_phantom, rng)

        # Specialization
        if tier == 1:
            spec_weights = SPECIALIZATION_WEIGHTS_TIER1
        elif tier == 2:
            spec_weights = SPECIALIZATION_WEIGHTS_TIER2
        else:
            spec_weights = SPECIALIZATION_WEIGHTS_TIER3
        specialization = rng.choice(HOSPITAL_SPECIALIZATIONS, p=spec_weights)

        # Empanelment date (phantom hospitals have shorter history)
        if is_phantom:
            days_back = rng.integers(30, 365)
        else:
            days_back = rng.integers(365, 3650)  # 1-10 years
        empanelment_date = (
            pd.Timestamp(CLAIM_START_DATE) - pd.Timedelta(days=int(days_back))
        ).strftime("%Y-%m-%d")

        records.append({
            "hospital_id": hospital_id,
            "name": name,
            "region": region,
            "city": city,
            "tier": tier,
            "is_phantom": is_phantom,
            "rohini_id": rohini_id,
            "empanelment_date": empanelment_date,
            "specialization": specialization,
            "total_claims_filed": 0,       # updated after claim gen
            "fraud_claims_ratio": 0.0,     # updated after claim gen
            "blacklisted": False,          # updated after fraud gen
        })

    return pd.DataFrame(records)
