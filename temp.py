from steps import ask_llm, fetch_user_preferences
from main_dbconnect import  initalize_db

db = initalize_db()
db.clear_all()
u = db.add_user("Aeelice", "aiee@ehmp.om", "hashed_passe", "Asia/Kolkata")
print({"added_user": u})
user_id = u['user_id']
pref = db.add_user_pref(user_id, 1000, 5000, "train", "relaxed")
# print({"added_pref": pref})
print({"prefs_by_user": db.get_prefs_by_user(user_id)})

int1 = db.add_interest(user_id, "food")
int2 = db.add_interest(user_id, "heritage")
get_interests_by_user = db.get_interests_by_user(user_id)
print({"interests_by_user": get_interests_by_user})


print(fetch_user_preferences(user_id))