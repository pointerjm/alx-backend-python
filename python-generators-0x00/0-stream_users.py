import mysql.connector

def stream_users():
    try:
        # Connect to the ALX_prodev database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Happy1473#",
            database="ALX_prodev"
        )
        # Create a cursor to execute the query
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            # Fetch rows one by one using a single loop
            for row in cursor:
                # Convert row to dictionary
                yield {
                    "user_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "age": row[3]
                }
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
        return  # Yield nothing on error