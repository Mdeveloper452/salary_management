from mysql.connector import (connection)
import os
from dotenv import load_dotenv
load_dotenv()
print("function work start")
print("trying to connect to database")
def db_connection():
    return connection.MySQLConnection(
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    database=os.getenv("MYSQL_DB")
    )
print("successfull connection")
