import mysql.connector
from mysql.connector import Error

# اطلاعات اتصال به دیتابیس
db_config = {
    "host": "localhost",
    "user": "wlcomco_user",
    "password": "4314314522P@ss"
}

# اتصال به MariaDB
try:
    connection = mysql.connector.connect(**db_config)
    if connection.is_connected():
        print("Connected to MariaDB.")

    cursor = connection.cursor()

    # ایجاد دیتابیس اگر وجود ندارد
    cursor.execute("CREATE DATABASE IF NOT EXISTS wlcomco_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print("Database 'wlcomco_db' checked/created.")

    # استفاده از دیتابیس
    cursor.execute("USE wlcomco_db;")

    # ایجاد جدول users اگر وجود ندارد
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fullname VARCHAR(255) NOT NULL,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        status ENUM('enable', 'disable') DEFAULT 'enable',
        role ENUM('admin', 'user') DEFAULT 'user'
    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    """
    cursor.execute(create_table_query)
    print("Table 'users' checked/created.")

    # بررسی و افزودن فیلدهای جدید در صورت عدم وجود
    fields_to_add = [
        {"name": "fullname", "definition": "VARCHAR(255) NOT NULL"},
        {"name": "username", "definition": "VARCHAR(255) UNIQUE NOT NULL"},
        {"name": "password", "definition": "VARCHAR(255) NOT NULL"},
        {"name": "status", "definition": "ENUM('enable', 'disable') DEFAULT 'enable'"},
        {"name": "role", "definition": "ENUM('admin', 'user') DEFAULT 'user'"}
    ]

    for field in fields_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {field['name']} {field['definition']};")
            print(f"Field '{field['name']}' added to 'users' table.")
        except mysql.connector.Error as err:
            if "Duplicate column name" in str(err):
                print(f"Field '{field['name']}' already exists.")
            else:
                print(f"Error adding field '{field['name']}': {err}")

except Error as e:
    print(f"Error connecting to MariaDB: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MariaDB connection closed.")
