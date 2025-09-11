import mysql.connector

def stream_users_in_batches(batch_size):
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
            # Fetch rows in batches using fetchmany
            while True:
                batch = cursor.fetchmany(batch_size)
                if not batch:
                    break
                # Yield each row in the batch as a dictionary
                for row in batch:
                    yield {
                        "user_id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "age": int(row[3])  # Cast age to int for consistency
                    }
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error streaming data: {err}")
        return  # Yield nothing on error

def batch_processing(batch_size):
    # Process batches and filter users over 25
    for user in stream_users_in_batches(batch_size):
        if user["age"] > 25:
            yield user