import os
import random
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import traceback
from faker import Faker
import json

# --- Import DB Config/Client ---
from db.baseDB import PostgresDB
from steps import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_SCHEMA

# --- Configuration ---
load_dotenv()

# Use Faker with Indian locale
fake = Faker("en_IN")

# User-provided names (MANDATORY LIST)
GIVEN_NAMES = ["Shubhankar", "Rujhil", "Sneha", "Ashwini", "Shriyansh", "Avikalp", "Neeraj", "Yash", "Satyam", "Srishti"]
LAST_NAME_SUFFIXES = ["Verma", "Rao", "Jain", "Mehta", "Patel", "Sharma"]

# Configure max lengths for known string columns (tune to match your schema)
MAX_LENGTHS = {
    "first_name": 50, "last_name": 50, "email": 255, "password_hash": 128, "dob": 20,
    "gender": 20, "aadhar_number": 20, "passport_number": 20, "driving_license_number": 30,
    "native_language": 50, "hometown": 100, "current_city": 100, "address": 255,
    "phone_number": 20, "dietary_preferences": 255, "tag": 50, "sub_tag": 50,
    "transport_pref": 50, "commute_pref": 50, "pace": 20, "travel_duration_preference": 50,
    "travel_group_preference": 50, "season_preference": 50, "accommodation_type": 50,
    "special_needs": 255,
}

# --- Data Templates ---
INDIAN_LOCATIONS = [
    {"city": "Mumbai", "lat": 19.0760, "lng": 72.8777, "address": "Bandra West, Mumbai"},
    {"city": "New Delhi", "lat": 28.6139, "lng": 77.2090, "address": "Hauz Khas, New Delhi"},
    {"city": "Bangalore", "lat": 12.9716, "lng": 77.5946, "address": "Koramangala, Bangalore"},
    {"city": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "address": "Hitech City, Hyderabad"},
    {"city": "Bhilai", "lat": 21.2217, "lng": 81.3850, "address": "Sector 6, Bhilai"},
]

INTEREST_TEMPLATES = [
    {"tag": "Food", "sub_tag": "Street Food", "activity_type": "Culinary Tour"},
    {"tag": "Culture", "sub_tag": "Heritage Sites", "activity_type": "Sightseeing"},
    {"tag": "Adventure", "sub_tag": "Trekking", "activity_type": "Hiking"},
    {"tag": "Relaxation", "sub_tag": "Beach", "activity_type": "Wellness"},
]

# --- Helpers ---
def safe_str(val, max_len):
    if val is None: return None
    s = str(val)
    if max_len is None or len(s) <= max_len: return s
    return s[:max_len]

def indian_aadhar():
    return "".join(str(random.randint(0, 9)) for _ in range(12))

def indian_passport():
    return random.choice("ABCDEFGH") + "".join(str(random.randint(0, 9)) for _ in range(7))

def indian_dl():
    state = random.choice(["MH", "DL", "KA", "UP", "TN", "WB", "RJ", "GJ"])
    return state + "".join(str(random.randint(0, 9)) for _ in range(12))

def indian_phone():
    first = str(random.choice([6,7,8,9]))
    rest = "".join(str(random.randint(0,9)) for _ in range(9))
    return "+91" + first + rest

def generate_user_data(name: str, index: int):
    first_name = safe_str(name, MAX_LENGTHS["first_name"])
    last_name = safe_str(random.choice(LAST_NAME_SUFFIXES), MAX_LENGTHS["last_name"])
    email = safe_str(f"{first_name.lower()}.{last_name.lower()}{index}@example.in", MAX_LENGTHS["email"])
    password_hash = safe_str(fake.sha256(), MAX_LENGTHS["password_hash"])

    location = INDIAN_LOCATIONS[index % len(INDIAN_LOCATIONS)]
    details = {
        "dob": safe_str(fake.date_of_birth(minimum_age=20, maximum_age=50).isoformat(), MAX_LENGTHS["dob"]),
        "gender": safe_str(random.choice(["Male", "Female"]), MAX_LENGTHS["gender"]),
        "aadhar_number": safe_str(indian_aadhar(), MAX_LENGTHS["aadhar_number"]),
        "passport_number": safe_str(indian_passport(), MAX_LENGTHS["passport_number"]),
        "driving_license_number": safe_str(indian_dl(), MAX_LENGTHS["driving_license_number"]),
        "spoken_languages": ["Gujrati"],
        "understood_languages": ["Hindi", "English"],
        "native_language": "Hindi",
        "hometown": safe_str(location["city"], MAX_LENGTHS["hometown"]),
        "current_city": safe_str(location["city"], MAX_LENGTHS["current_city"]),
        "address": safe_str(location["address"], MAX_LENGTHS["address"]),
        "phone_number": safe_str(indian_phone(), MAX_LENGTHS["phone_number"]),
        "home_lat": location["lat"] + random.uniform(-0.01, 0.01),
        "home_lng": location["lng"] + random.uniform(-0.01, 0.01),
        "dietary_preferences": random.choice([["Vegetarian", "No Nuts"], ["Non-Vegetarian"], ["Vegan"], ["Jain"], ["No Dairy"]])
    }

    travel_pref = {
        "budget_min": random.randint(500, 2000),
        "budget_max": random.randint(3000, 15000),
        "transport_pref": safe_str(random.choice(["Car", "Train", "Flight"]), MAX_LENGTHS["transport_pref"]),
        "commute_pref": safe_str(random.choice(["Metro", "Auto", "Drive"]), MAX_LENGTHS["commute_pref"]),
        "pace": safe_str(random.choice(["Relaxed", "Moderate", "Fast"]), MAX_LENGTHS["pace"]),
        "travel_duration_preference": safe_str(random.choice(["Weekend", "1 week", "2-5 days"]), MAX_LENGTHS["travel_duration_preference"]),
        "travel_group_preference": safe_str(random.choice(["Solo", "Friends", "Family"]), MAX_LENGTHS["travel_group_preference"]),
        "preferred_regions": [safe_str(fake.state(), 50) for _ in range(2)],
        "season_preference": safe_str(random.choice(["Winter", "Summer"]), MAX_LENGTHS["season_preference"]),
        "accommodation_type": safe_str(random.choice(["Hotel", "Hostel", "Airbnb"]), MAX_LENGTHS["accommodation_type"]),
        "frequent_travel": random.choice([True, False]),
    }

    interests = random.sample(INTEREST_TEMPLATES, 2)

    return first_name, last_name, email, password_hash, details, interests, travel_pref

def truncate_details(details: dict):
    truncated = {}
    for k, v in details.items():
        max_len = MAX_LENGTHS.get(k, None)
        if isinstance(v, (int, float, list, dict)) or v is None:
            truncated[k] = v
        else:
            truncated[k] = safe_str(v, max_len)
    return truncated

# ----------------- Population Executor ----------------- #

def populate_database(db: PostgresDB, count: int):
    """
    Populates exactly `count` users. If count > len(GIVEN_NAMES),
    the name list is cycled/duplicated to meet the requested count.
    """
    # If you do NOT want to wipe existing test data, comment the next line
    db.clear_all()
    print(f"Starting population of {count} custom users...")

    # Prepare names: ensure we use the exact list first, then fill if needed
    names_to_use = GIVEN_NAMES + random.choices(GIVEN_NAMES, k=max(0, count - len(GIVEN_NAMES)))

    created = 0
    for i, name in enumerate(names_to_use[:count]):
        try:
            first_name, last_name, email, pwd, details, interests, travel_pref = generate_user_data(name, i)

            user = db.add_user(
                first_name=safe_str(first_name, MAX_LENGTHS["first_name"]),
                last_name=safe_str(last_name, MAX_LENGTHS["last_name"]),
                email=safe_str(email, MAX_LENGTHS["email"]),
                password_hash=safe_str(pwd, MAX_LENGTHS["password_hash"])
            )
            user_id = user["user_id"]

            details_trunc = truncate_details(details)
            db.add_user_details(user_id=user_id, **details_trunc)

            # pref truncate (only string fields get truncated via truncate_details)
            pref_trunc = truncate_details(travel_pref)
            db.add_travel_preference(user_id=user_id, **pref_trunc)

            # interests
            for intr in interests:
                db.add_user_interest(
                    user_id=user_id,
                    tag=safe_str(intr.get("tag"), MAX_LENGTHS["tag"]),
                    sub_tag=safe_str(intr.get("sub_tag"), MAX_LENGTHS["sub_tag"]),
                    preferred_vacation_type=safe_str(intr.get("preferred_vacation_type", ""), 50) if intr.get("preferred_vacation_type") else None,
                    activity_type=safe_str(intr.get("activity_type"), 50),
                    frequency_of_interest=None,
                    special_notes=None
                )

            print(f"✅ User {created+1}: {first_name} {last_name} ({user_id[:8]}) added.")
            created += 1

        except Exception as e:
            print(f"❌ Failed to insert user {name}. Error: {e}")
            # traceback.print_exc()  # enable if you want full stack trace

    print(f"\n🎉 Successfully created {created}/{count} users.")
    res = db.execute_query("SELECT COUNT(*) AS cnt FROM users;", fetch="one")
    print(f"Total users in DB now: {res['cnt']}")

def main_executor(count=10):
    db = None
    try:
        db = PostgresDB(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        db.connect(schema=DB_SCHEMA)
        populate_database(db, count)
    except Exception as e:
        print("\n--- FATAL ERROR ---")
        print("Could not complete database population. Please check DB config and connectivity.")
        print("Error details:", e)
    finally:
        if db and getattr(db, 'conn', None):
            db.close()

if __name__ == "__main__":
    # default: populate 10 (the exact given list)
    main_executor(count=10)
