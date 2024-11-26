from db import get_db_connection

# تابع برای دریافت لیست کاربران
def get_all_users():
    connection = get_db_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, fullname, username, status, role FROM users;")
        users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []
    finally:
        cursor.close()
        connection.close()
