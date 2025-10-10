from db.baseDB import PostgresDB
from steps import add_demo_data
DB_HOST = "10.144.192.33"  
DB_NAME = "map_assistant" 
DB_USER = "postgres"
DB_PASSWORD = "1214" 
DB_SCHEMA = "public"


DB_PORT = 5432

# MY

# DB_HOST = "localhost"
# DB_NAME = "Try"
# DB_USER = "postgres"
# DB_PASSWORD = "jojo"
# DB_SCHEMA = "mapassitant"

_db_client = None

def initialize_db_client_new():
    global _db_client 
    _db_client = PostgresDB(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    _db_client.connect(schema=DB_SCHEMA)

    return _db_client

# initialize_db_client_new()
# _db_client.test()


add_demo_data()