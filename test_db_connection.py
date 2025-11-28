from steps import run_sql
from steps import initialize_db_client

db = initialize_db_client()
user_id = "22bb4f93-26a1-4bcd-8c27-5ef7b078d679"
user_id = "206c17a2-5721-4092-b8b0-9c09134e549a"

sql = f"""SELECT * FROM users WHERE user_id = '{user_id}';"""
# db.execute_query(sql)

print(run_sql(sql,"one"))

print(sql)
# print(run_sql(sql,"one"))