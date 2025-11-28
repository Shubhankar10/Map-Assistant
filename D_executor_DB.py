from steps import run_sql
from steps import initialize_db_client

db = initialize_db_client()
user_id = "22bb4f93-26a1-4bcd-8c27-5ef7b078d679"

sql = f"""SELECT * FROM users WHERE user_id = '{user_id}';"""
# db.execute_query(sql)

print(sql)
print(run_sql(sql,"one"))