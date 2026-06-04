"""
generators/patient_gen.py
Generate realistic Indian patient profiles with regional language names,
age-correlated conditions, and KYC verification data.
"""

import numpy as np
import pandas as pd
from faker import Faker

from config import (
    LANGUAGE_WEIGHTS,
    KYC_TYPES,
    KYC_TYPE_WEIGHTS,
    AGE_MEAN,
    AGE_STD,
    AGE_MIN,
    AGE_MAX,
    PRE_EXISTING_CONDITIONS,
    CLAIM_START_DATE,
    RANDOM_SEED,
)

fake = Faker("en_IN")
Faker.seed(RANDOM_SEED)

# ─── Language Pools ───────────────────────────────────────────────────────────
# Each language has: first names (native + romanized), last names, states
LANGUAGE_POOLS = {
    "hindi": {
        "first_names_male": [
            "राहुल", "अमित", "सुनील", "विकास", "रोहित", "अजय", "संजय", "मनोज",
            "दीपक", "प्रवीण", "Rahul", "Amit", "Sunil", "Vikas", "Rohit",
            "Ajay", "Sanjay", "Manoj", "Deepak", "Praveen",
        ],
        "first_names_female": [
            "प्रिया", "सुनीता", "अनीता", "रीना", "पूजा", "नेहा", "स्वाति", "काव्या",
            "Priya", "Sunita", "Anita", "Reena", "Pooja", "Neha", "Swati", "Kavya",
        ],
        "last_names": [
            "शर्मा", "गुप्ता", "सिंह", "वर्मा", "मिश्रा", "पांडे", "त्रिपाठी",
            "Sharma", "Gupta", "Singh", "Verma", "Mishra", "Pandey", "Tripathi",
            "Yadav", "Tiwari", "Chauhan", "Rajput",
        ],
        "states": [
            "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Bihar",
            "Jharkhand", "Uttarakhand", "Chhattisgarh", "Delhi",
        ],
    },
    "tamil": {
        "first_names_male": [
            "முருகன்", "கார்த்திக்", "செல்வம்", "அருண்", "பிரகாஷ்",
            "Murugan", "Karthik", "Selvam", "Arun", "Prakash",
            "Senthil", "Vijay", "Kumar", "Rajan", "Ganesh",
        ],
        "first_names_female": [
            "லக்ஷ்மி", "சரஸ்வதி", "மீனா", "காவ்யா", "தீபா",
            "Lakshmi", "Saraswati", "Meena", "Kavya", "Deepa",
            "Priya", "Revathi", "Sangeetha", "Anitha",
        ],
        "last_names": [
            "நாயுடு", "முதலியார்", "பிள்ளை", "அய்யர்",
            "Naidu", "Mudaliar", "Pillai", "Iyer", "Iyengar",
            "Chettiar", "Gounder", "Thevar", "Rajan",
        ],
        "states": ["Tamil Nadu", "Puducherry"],
    },
    "telugu": {
        "first_names_male": [
            "వెంకటేష్", "రాజేష్", "సురేష్", "మహేష్", "రమేష్",
            "Venkatesh", "Rajesh", "Suresh", "Mahesh", "Ramesh",
            "Srinivas", "Narasimha", "Ravi", "Krishna", "Prasad",
        ],
        "first_names_female": [
            "లక్ష్మి", "సీత", "పద్మ", "విజయ", "అనిత",
            "Lakshmi", "Sita", "Padma", "Vijaya", "Anitha",
            "Swathi", "Divya", "Bhavani", "Jyothi",
        ],
        "last_names": [
            "రెడ్డి", "నాయుడు", "రావు", "శర్మ",
            "Reddy", "Naidu", "Rao", "Sharma", "Chowdary",
            "Goud", "Varma", "Murthy", "Prasad",
        ],
        "states": ["Telangana", "Andhra Pradesh"],
    },
    "bengali": {
        "first_names_male": [
            "সুভাষ", "অমিত", "রাজেশ", "দেবাশীষ", "প্রদীপ",
            "Subhash", "Amit", "Rajesh", "Debashish", "Pradeep",
            "Sourav", "Arnab", "Partha", "Dipak", "Bikash",
        ],
        "first_names_female": [
            "স্বাতি", "মিতা", "রীনা", "সোমা", "পূর্ণিমা",
            "Swati", "Mita", "Reena", "Soma", "Purnima",
            "Moumita", "Sayantani", "Tanushree", "Arpita",
        ],
        "last_names": [
            "বন্দ্যোপাধ্যায়", "চক্রবর্তী", "দাস", "ঘোষ",
            "Banerjee", "Chakraborty", "Das", "Ghosh", "Sen",
            "Bose", "Roy", "Mukherjee", "Dutta", "Saha",
        ],
        "states": ["West Bengal", "Tripura"],
    },
    "marathi": {
        "first_names_male": [
            "सचिन", "विनोद", "अमोल", "संदीप", "राजेश",
            "Sachin", "Vinod", "Amol", "Sandeep", "Rajesh",
            "Prashant", "Sudhir", "Mangesh", "Ganesh", "Nitin",
        ],
        "first_names_female": [
            "स्मिता", "सुप्रिया", "प्राची", "रश्मी", "ज्योती",
            "Smita", "Supriya", "Prachi", "Rashmi", "Jyoti",
            "Anjali", "Madhuri", "Shruti", "Vaishali",
        ],
        "last_names": [
            "पाटील", "कुलकर्णी", "देशमुख", "जोशी",
            "Patil", "Kulkarni", "Deshmukh", "Joshi", "Shinde",
            "Jadhav", "More", "Pawar", "Chavan", "Kadam",
        ],
        "states": ["Maharashtra", "Goa"],
    },
    "gujarati": {
        "first_names_male": [
            "ધીરજ", "મુકેશ", "હર્ષ", "જયેશ", "કેતન",
            "Dhiraj", "Mukesh", "Harsh", "Jayesh", "Ketan",
            "Nilesh", "Rakesh", "Bhavesh", "Chirag", "Darshan",
        ],
        "first_names_female": [
            "હેતલ", "ખુશ્બુ", "દીપ્તિ", "પ્રીતિ", "કૃતિ",
            "Hetal", "Khushbu", "Dipti", "Priti", "Kriti",
            "Nisha", "Minal", "Sweta", "Falguni",
        ],
        "last_names": [
            "પટેલ", "શાહ", "મહેતા", "દેસાઈ",
            "Patel", "Shah", "Mehta", "Desai", "Modi",
            "Trivedi", "Bhatt", "Joshi", "Dave", "Thakkar",
        ],
        "states": ["Gujarat", "Dadra and Nagar Haveli"],
    },
    "punjabi": {
        "first_names_male": [
            "ਹਰਪ੍ਰੀਤ", "ਗੁਰਪ੍ਰੀਤ", "ਅਮਰਿੰਦਰ", "ਮਨਪ੍ਰੀਤ", "ਜਸਪ੍ਰੀਤ",
            "Harpreet", "Gurpreet", "Amarinder", "Manpreet", "Jaspreet",
            "Sukhdev", "Balwinder", "Kuldeep", "Navjot", "Satinder",
        ],
        "first_names_female": [
            "ਸਿਮਰਨ", "ਹਰਲੀਨ", "ਜਸਮੀਨ", "ਪਰਮਜੀਤ", "ਰੁਪਿੰਦਰ",
            "Simran", "Harleen", "Jasmeen", "Paramjeet", "Rupinder",
            "Navneet", "Kirandeep", "Amandeep", "Gurleen",
        ],
        "last_names": [
            "ਸਿੰਘ", "ਕੌਰ", "ਗਿੱਲ", "ਸਿੱਧੂ",
            "Singh", "Kaur", "Gill", "Sidhu", "Sandhu",
            "Grewal", "Dhillon", "Brar", "Mann", "Bajwa",
        ],
        "states": ["Punjab", "Haryana", "Chandigarh"],
    },
}


def _generate_pre_existing(age: int, rng: np.random.Generator) -> str:
    """Generate age-correlated pre-existing conditions."""
    if age < 30:
        # 90% chance of no conditions
        if rng.random() < 0.90:
            return "none"
        return rng.choice(["asthma", "thyroid_disorder"])
    elif age < 50:
        # 60% chance of no conditions
        if rng.random() < 0.60:
            return "none"
        n = rng.integers(1, 3)
        conditions = rng.choice(PRE_EXISTING_CONDITIONS, size=n, replace=False)
        return ",".join(conditions)
    else:
        # 30% chance of no conditions
        if rng.random() < 0.30:
            return "none"
        n = rng.integers(1, 5)
        conditions = rng.choice(PRE_EXISTING_CONDITIONS, size=n, replace=False)
        return ",".join(conditions)


def generate_patients(n_patients: int, rng: np.random.Generator) -> pd.DataFrame:
    """Generate n_patients Indian patient profiles."""
    languages = list(LANGUAGE_WEIGHTS.keys())
    lang_weights = list(LANGUAGE_WEIGHTS.values())

    records = []
    for i in range(n_patients):
        patient_id = f"P{i+1:06d}"

        # Pick language based on weights
        language = rng.choice(languages, p=lang_weights)
        pool = LANGUAGE_POOLS[language]

        # Gender
        gender = rng.choice(["male", "female"], p=[0.52, 0.48])

        # Name
        if gender == "male":
            first_name = rng.choice(pool["first_names_male"])
        else:
            first_name = rng.choice(pool["first_names_female"])
        last_name = rng.choice(pool["last_names"])
        name = f"{first_name} {last_name}"

        # State
        state = rng.choice(pool["states"])

        # Age (Gaussian, clamped)
        age = int(np.clip(rng.normal(AGE_MEAN, AGE_STD), AGE_MIN, AGE_MAX))

        # KYC
        kyc_type = rng.choice(KYC_TYPES, p=KYC_TYPE_WEIGHTS)
        identity_verified = rng.random() < 0.92  # 92% verified

        # Pre-existing conditions
        pre_existing = _generate_pre_existing(age, rng)

        # Policy start date (random within 5 years before claim window)
        days_back = rng.integers(30, 1825)
        policy_start = pd.Timestamp(CLAIM_START_DATE) - pd.Timedelta(days=int(days_back))

        records.append({
            "patient_id": patient_id,
            "name": name,
            "language": language,
            "age": age,
            "gender": gender,
            "state": state,
            "policy_start_date": policy_start.strftime("%Y-%m-%d"),
            "pre_existing_conditions": pre_existing,
            "number_of_claims_lifetime": 0,   # updated after claim gen
            "number_of_claims_last_12m": 0,   # updated after claim gen
            "average_claim_amount": 0.0,       # updated after claim gen
            "identity_verified": identity_verified,
            "kyc_type": kyc_type,
        })

    return pd.DataFrame(records)
