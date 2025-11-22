from steps import ask_llm

import json
import re
from typing import Dict


class NewFederator:
    def __init__(self, context: dict, user_db_schema: dict):
        self.context = context
        self.schema = user_db_schema

    def _build_prompt(self):
        prompt = f"""
You are a Federator module that generates structured data for downstream tasks.

### INPUT CONTEXT
{self.context}

### USER DB SCHEMA (fields available in DB)
{self.schema}

### YOUR TASK
You must return a JSON with EXACTLY these 3 keys:

1. "DB_Map":
   A dictionary mapping from UserDB schema keyword → context keyword.
   - Example:
       "budget": "total_budget"
       "travel_pace": "travel_speed"
   - Only map all meaning which are same or similar.
   - Use best semantic judgement.

2. "DB_Data":
   A list of schema keywords relevant to:
      - user_intent from the context
      - the details in context
      - original query
    include all the keywords from the schema which are relevant to the context.

3. "POI_Queries":
   A list of Google Places API queries needed to complete the task.
   These should be strings fully formed.
   example: "historical places in Jaipur near Amer Fort",
    for all must_see POIs from context build a string like : "Details about [place] in [city], and nearby POIs"
    for all preferred cuisines from context build a string like : "Best [cuisine] restaurants in [city] near [landmark]"
    for all activities from context build a string like : "Popular [activity] spots in [city]."
    for all interests from context build a string like : "Best places for tourists to enjoy [interest] of the [city]".strip()

### RULES
- Output ONLY valid JSON.
- No extra text.
- Make mappings only if meanings match.
- POI queries should be descriptive.

Return JSON now.
"""
        return prompt

    def run(self):
        prompt = self._build_prompt()
        response = ask_llm(prompt)
        return response  # assumed to already be parsed JSON


if __name__ == "__main__":

    sample_context = {
      "task_type": "travel_itinerary",
      "original_query": "Plan a 2 day itinerary in Jaipur covering Amer Fort and City Palace with a budget of 5000 INR.",
      "user_intent": "Create a detailed two-day travel plan for Jaipur that includes visits to Amer Fort and City Palace, adhering to a total budget of 5000 Indian Rupees.",
      "mandatory_fields": [
        "destination",
        "duration_days",
        "attractions",
        "total_budget",
        "start_date",
        "end_date",
        "accommodation",
        "transportation"
      ],
      "details": {
        "destination": "Jaipur",
        "duration_days": 2,
        "attractions": ["Amer Fort", "City Palace"],
        "total_budget": 5000,
        "currency": "INR",
        "start_date": None,
        "end_date": None,
        "accommodation": None,
        "transportation": None,
        "meals": None,
        "other_activities": None
      }
    }

    sample_schema = {
        # --- user table ---
        "first_name": "string",
        "last_name": "string",
        "email": "string",
        "password_hash": "string",
        "created_at": "datetime",

        # --- details table ---
        "dob": "date",
        "gender": "string",
        "aadhar_number": "string",
        "passport_number": "string",
        "driving_license_number": "string",
        "spoken_languages": "list[string]",
        "understood_languages": "list[string]",
        "native_language": "string",
        "hometown": "string",
        "current_city": "string",
        "address": "string",
        "phone_number": "string",
        "home_lat": "float",
        "home_lng": "float",
        "dietary_preferences": "list[string]",

        # --- preferences table ---
        "budget_min": "float",
        "budget_max": "float",
        "transport_pref": "string",
        "commute_pref": "string",
        "pace": "string",
        "travel_duration_preference": "string",
        "travel_group_preference": "string",
        "preferred_regions": "list[string]",
        "season_preference": "string",
        "accommodation_type": "string",
        "special_needs": "string_or_null",
        "frequent_travel": "boolean",

        # --- interests table (list of interest rows) ---
        "tag": "string",
        "sub_tag": "string",
        "preferred_vacation_type": "string",
        "activity_type": "string",
        "frequency_of_interest": "string",
        "special_notes": "string"
    }



    federator = Federator(sample_context, sample_schema)
    output = federator.run()

    print("\n=== FINAL OUTPUT ===")
    print(output)
