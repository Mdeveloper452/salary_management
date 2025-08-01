from mysql.connector import (connection)
import os
from dotenv import load_dotenv
load_dotenv()

def db_connection():
    return connection.MySQLConnection(
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DB")
    )
print("successfull connection")
