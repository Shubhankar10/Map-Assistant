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
    u = db.add_user("Aeelice", "alicere@example.com", "hashed_passe", "Asia/Kolkata")
    pprint({"added_user": u})

    user_id = u['user_id']
    pprint({"get_by_id": db.get_user_by_id(user_id)})
    pprint({"get_by_email": db.get_user_by_email("alice@example.com")})
    pprint({"all_users": db.get_all_users(limit=10)})

    db.update_user(user_id, {"name": "Alice Updated", "timezone": "Asia/Kolkata"})
    pprint({"after_update": db.get_user_by_id(user_id)})

    # ---------- PREFERENCES ----------
    pref = db.add_user_pref(user_id, 1000, 5000, "train", "relaxed")
    pprint({"added_pref": pref})
    pprint({"prefs_by_user": db.get_prefs_by_user(user_id)})
    db.update_pref(pref['pref_id'], {"budget_min": 1500})
    pprint({"pref_after_update": db.get_pref_by_id(pref['pref_id'] )})

    # ---------- INTERESTS ----------
    int1 = db.add_interest(user_id, "food")
    int2 = db.add_interest(user_id, "heritage")
    pprint({"added_interests": [int1, int2]})
    pprint({"interests_by_user": db.get_interests_by_user(user_id)})
    db.update_interest(int1['interest_id'], "local_food")
    pprint({"interest_after_update": db.get_interest_by_id(int1['interest_id'])})

    # ---------- TRIPS ----------
    trip = db.add_trip(user_id, "Weekend Delhi", "Delhi", "2025-09-20", "2025-09-21")
    pprint({"added_trip": trip})
    trip_id = trip['trip_id']
    pprint({"trips_by_user": db.get_trips_by_user(user_id)})
    db.update_trip(trip_id, {"title": "Weekend Delhi Updated", "status": "active"})
    pprint({"trip_after_update": db.get_trip_by_id(trip_id)})
    pprint({"recent_trips": db.get_recent_trips(limit=5)})
    pprint({"search_trips_city_delhi": db.search_trips_by_city("delhi")})

    # ---------- ITINERARIES ----------
    itin = db.add_itinerary(trip_id, 1, 1, "India Gate", "Rajpath", "2025-09-20 10:00", "2025-09-20 12:00", "Sightseeing")
    pprint({"added_itinerary": itin})
    pprint({"itineraries_by_trip": db.get_itineraries_by_trip(trip_id)})
    db.update_itinerary(itin['itinerary_id'], {"notes": "Buy tickets online"})
    pprint({"itinerary_after_update": db.get_itinerary_by_id(itin['itinerary_id'])})

    # ---------- JOURNALS ----------
    journal = db.add_journal(trip_id, 1, "Great day exploring!", '{"photos":["img1.jpg"]}')
    pprint({"added_journal": journal})
    pprint({"journals_by_trip": db.get_journals_by_trip(trip_id)})
    pprint({"journals_by_user": db.get_journals_by_user(user_id)})
    db.update_journal(journal['journal_id'], {"entry_text": "Even better day!"})
    pprint({"journal_after_update": db.get_journal_by_id(journal['journal_id'])})

    # ---------- COMPOSITES ----------
    pprint({"user_full_profile": db.get_user_full_profile(user_id)})
    pprint({"trip_full_details": db.get_trip_full_details(trip_id)})

    # ---------- DELETES (cleanup) ----------
    db.delete_journal(journal['journal_id'])
    db.delete_itinerary(itin['itinerary_id'])
    db.delete_trip(trip_id)
    db.delete_interest(int1['interest_id'])
    db.delete_interest(int2['interest_id'])
    db.delete_pref(pref['pref_id'])
    db.delete_user(user_id)

    print("Counts after cleanup:")
    print("users:", db.count_rows("users"))
    print("trips:", db.count_rows("trips"))


    db.execute_query("SELECT * FROM users WHERE user_id = %s;", (user_id,), fetchone=True)


    # db.execute_query(""" SELECT 'user_details' AS table_name, to_json(users) AS row_data FROM users WHERE user_id = %s
    #                  UNION ALL SELECT 'user_interests' AS table_name, to_json(user_interests) AS row_data FROM user_interests WHERE user_id = %s 
    #                  UNION ALL SELECT 'travel_preferences' AS table_name, to_json(travel_preferences) AS row_data FROM travel_preferences WHERE user_id = %s """,(user_id,user_id,user_id))
    
    db.clear_all()
    db.close()


if __name__ == "__main__":
    main()
