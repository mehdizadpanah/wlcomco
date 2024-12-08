import mysql.connector
from mysql.connector import Error

# تابع برای اتصال به دیتابیس
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="wlcomco_user",
            password="4314314522P@ss",
            database="wlcomco_db"
        )
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None
