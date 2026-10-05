import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ["LANGGRAPH_DB_URL"]

with psycopg.connect(db_url) as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                current_database(),
                current_user,
                version()
            """
        )
        database, user, version = cursor.fetchone()

print("database:", database)
print("user:", user)
print("version:", version)