import seed

def paginate_users(page_size, offset):
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows

def lazy_paginate(page_size):
    offset = 0
    while True:
        # Fetch the next page using paginate_users
        page = paginate_users(page_size, offset)
        if not page:
            break
        # Yield the entire page (list of dictionaries)
        yield page
        offset += page_size