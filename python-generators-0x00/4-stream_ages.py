import mysql.connector

def stream_user_ages():
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
            cursor.execute("SELECT age FROM user_data")
            # Yield ages one by one
            for row in cursor:
                yield int(row[0])  # Cast age to int
        connection.close()
    except mysql.connector.Error as err:
        print(f"Error streaming ages: {err}")
        return  # Yield nothing on error

def calculate_average_age():
    total_age = 0
    count = 0
    # Use generator to accumulate sum and count
    for age in stream_user_ages():
        total_age += age
        count += 1
    # Calculate average, handling empty dataset
    average = total_age / count if count > 0 else 0
    return average

if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age}")