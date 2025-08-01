from mysql.connector import (connection)
import os
from dotenv import load_dotenv
load_dotenv()
print("function work start")
print("trying to connect to database")
print("Trying to connect to DB with values:")
print("User:", os.getenv("MYSQL_USER"))
print("Password:", os.getenv("MYSQL_PASSWORD"))
print("Host:", os.getenv("MYSQL_HOST"))
print("Port:", os.getenv("MYSQL_PORT"))
print("Database:", os.getenv("MYSQL_DB"))
def db_connection():
    return connection.MySQLConnection(
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DB")
    )
print("successfull connection")
