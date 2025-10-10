# example_main.py
from db.baseDB import PostgresDB
from pprint import pprint
from steps import initialize_db_client

def main():

    # db = PostgresDB(host="localhost", dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    # db.connect(schema=DB_SCHEMA)
    db = initialize_db_client()

    # db.clear_all() 

    # ---------- USERS ----------
    # Sample call to add a new user
    new_user = db.add_user(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password_hash="hashed_password_here"
    )
    print(new_user)  # Returns the inserted user record

    user_id = new_user['user_id']  # Assuming the DB returns user_id

    # Sample call to get a user by ID
    user_record = db.get_user_by_id(user_id)
    print(user_record)  # Returns the user record with this ID

    # Sample call to delete a user
    deleted_count = db.delete_user(user_id)
    print(f"Number of users deleted: {deleted_count}")

    # ---------- Interests ----------
    # Sample call to add user details
    user_details = db.add_user_details(
        user_id=user_id,
        dob="1990-05-15",
        gender="Male",
        aadhar_number="1234-5678-9012",
        passport_number="M1234567",
        driving_license_number="DL1234567890",
        spoken_languages=["English", "Hindi"],
        understood_languages=["English", "Hindi", "French"],
        native_language="Hindi",
        hometown="Jaipur",
        current_city="Delhi",
        address="123 Main Street",
        phone_number="+911234567890",
        home_lat=26.9124,
        home_lng=75.7873,
        dietary_preferences=["Vegetarian", "No Nuts"]
    )
    print(user_details)  # Returns the inserted user_details record

    # Sample call to get user details by ID
    details_record = db.get_user_details_by_id(user_id)
    print(details_record)  # Returns the user_details record

    # Sample call to delete user details
    deleted_details_count = db.delete_user_details(user_id)
    print(f"Number of user_details deleted: {deleted_details_count}")



    # ---------- TRAVEL PREF ----------

    # Sample call to add a travel preference
    travel_pref = db.add_travel_preference(
        user_id=user_id,
        budget_min=500.00,
        budget_max=1500.00,
        transport_pref="Car",
        commute_pref="Metro",
        pace="Balanced",
        travel_duration_preference="2-5 days",
        travel_group_preference="Family",
        preferred_regions=["Rajasthan", "Uttar Pradesh"],
        season_preference="Winter",
        accommodation_type="Hotel",
        special_needs="Wheelchair accessible",
        frequent_travel=True
    )
    print(travel_pref)  # Returns the inserted travel_preferences record

    # Sample call to get travel preference by user_id
    pref_record = db.get_travel_preference_by_user_id(user_id)
    print(pref_record)  # Returns the travel_preferences record for this user

    # Sample call to delete travel preference by user_id
    deleted_count = db.delete_travel_preference(user_id)
    print(f"Number of travel_preferences deleted: {deleted_count}")

        # USER interest----------------------------------
    # Add a user interest
    interest = db.add_user_interest(
        user_id=user_id,
        tag="Food",
        sub_tag="Street Food",
        preferred_vacation_type="City Break",
        activity_type="Culinary Tour",
        frequency_of_interest="Often",
        special_notes="Prefers vegetarian options"
    )
    print(interest)

    # Get all interests for a user
    all_interests = db.get_user_interests_by_user_id(user_id)
    print(all_interests)

    # Delete a specific interest by interest_id
    deleted_count = db.delete_user_interest(interest['interest_id'])
    print(f"Number of user_interests deleted: {deleted_count}")



    #TRIPS--------------------------------------------------------------------------

    # Sample call to add a trip
    new_trip = db.add_trip(
        user_id=user_id,
        title="Jaipur Weekend Getaway",
        city="Jaipur",
        country="India",
        start_date="2025-11-01",
        end_date="2025-11-03",
        status="draft",
        description="A cultural and culinary trip to Jaipur",
        trip_type="Leisure",
        total_budget=1200.00,
        transport_mode_to_city="Car",
        accommodation_type="Hotel",
        tags={"interests": ["heritage", "food"]},
        rating=None,
        favorite_locations={"places_to_visit": ["Amber Fort", "City Palace"]}
    )
    print(new_trip)

    # Sample call to get a trip by ID
    trip_record = db.get_trip_by_id(new_trip['trip_id'])
    print(trip_record)

    # Sample call to delete a trip
    deleted_count = db.delete_trip(new_trip['trip_id'])
    print(f"Number of trips deleted: {deleted_count}")




    # ==============================
    # TRIP JOURNALS SAMPLE CALLS
    # ==============================

    # Add a trip journal entry
    journal_entry = db.add_trip_journal(
        trip_id=new_trip['trip_id'],
        day=1,
        entry_text="Visited Amber Fort and City Palace. Enjoyed local Rajasthani cuisine.",
        location={"lat": 26.9124, "lng": 75.7873},
        tags={"type": "sightseeing"},
        expenses={"total": 500, "currency": "INR"},
        visited_places={"Amber Fort": "10:00-12:00", "City Palace": "12:30-14:00"},
        recommended_for_next_time="Explore Jaipur markets",
        mood="Excited",
        travel_companions={"family": ["John", "Jane"]},
        transportation_used={"mode": "Car"},
        summary_generated="Visited major forts and palaces, enjoyed local food.",
        recommendations_generated="Next time, visit markets and light shows."
    )
    print(journal_entry)

    # Get all journals for a trip
    journals = db.get_trip_journals_by_trip_id(new_trip['trip_id'])
    print(journals)

    # Delete a journal entry
    deleted_journal_count = db.delete_trip_journal(journal_entry['journal_id'])
    print(f"Number of journal entries deleted: {deleted_journal_count}")


    # ==============================
    # ITINERARIES SAMPLE CALLS
    # ==============================

    # Add an itinerary for the trip
    itinerary_entry = db.add_itinerary(
        trip_id=new_trip['trip_id'],
        days=2,
        pois={
            "day_1": [
                {"name": "Amber Fort", "lat": 26.9855, "lng": 75.8511, "start_time": "09:00", "end_time": "11:30"},
                {"name": "City Palace", "lat": 26.9258, "lng": 75.8240, "start_time": "12:00", "end_time": "14:00"}
            ],
            "day_2": [
                {"name": "Hawa Mahal", "lat": 26.9239, "lng": 75.8267, "start_time": "10:00", "end_time": "11:30"},
                {"name": "Jal Mahal", "lat": 26.9512, "lng": 75.8143, "start_time": "12:00", "end_time": "13:00"}
            ]
        }
    )
    print(itinerary_entry)

    # Get all itineraries for a trip
    itineraries = db.get_itineraries_by_trip_id(new_trip['trip_id'])
    print(itineraries)

    # Delete an itinerary
    deleted_itinerary_count = db.delete_itinerary(itinerary_entry['itinerary_id'])
    print(f"Number of itineraries deleted: {deleted_itinerary_count}")






















    print("Counts after cleanup:")
    print("users:", db.count_rows("users"))


    db.execute_query("SELECT * FROM users WHERE user_id = %s;", (user_id,), fetchone=True)


    # db.execute_query(""" SELECT 'user_details' AS table_name, to_json(users) AS row_data FROM users WHERE user_id = %s
    #                  UNION ALL SELECT 'user_interests' AS table_name, to_json(user_interests) AS row_data FROM user_interests WHERE user_id = %s 
    #                  UNION ALL SELECT 'travel_preferences' AS table_name, to_json(travel_preferences) AS row_data FROM travel_preferences WHERE user_id = %s """,(user_id,user_id,user_id))
    
    db.clear_all()
    db.close()


if __name__ == "__main__":
    main()
