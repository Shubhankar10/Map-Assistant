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
        email="john.doe@moxl.com",
        password_hash="hashed_password_here"
    )
    print(new_user)  # Returns the inserted user record

    user_id = new_user['user_id']  # Assuming the DB returns user_id

    # Sample call to get a user by ID
    user_record = db.get_user_by_id(user_id)
    print(user_record)  # Returns the user record with this ID

    # Sample call to delete a user
    # deleted_count = db.delete_user(user_id)
    # print(f"Number of users deleted: {deleted_count}")

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
    # deleted_details_count = db.delete_user_details(user_id)
    # print(f"Number of user_details deleted: {deleted_details_count}")



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
    # deleted_count = db.delete_travel_preference(user_id)
    # print(f"Number of travel_preferences deleted: {deleted_count}")

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
    # deleted_count = db.delete_user_interest(interest['interest_id'])
    # print(f"Number of user_interests deleted: {deleted_count}")


    print("\n\n\n")
    # db.execute_query(""" SELECT 'user_details' AS table_name, to_json(users) AS row_data FROM users WHERE user_id = %s
    #                  UNION ALL SELECT 'user_interests' AS table_name, to_json(user_interests) AS row_data FROM user_interests WHERE user_id = %s 
    #                  UNION ALL SELECT 'travel_preferences' AS table_name, to_json(travel_preferences) AS row_data FROM travel_preferences WHERE user_id = %s """,(user_id,user_id,user_id))
    print(db.get_user_full_profile(user_id))

    
    db.clear_all()
    db.close()


if __name__ == "__main__":
    main()

