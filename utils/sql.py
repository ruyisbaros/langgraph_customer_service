import sqlite3
from icecream import ic as print


# DB connection Function
def get_conn(db_name):
    try:
        return sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def create_flights_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS flights(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheduled_departure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scheduled_arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actual_departure TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actual_arrival TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    try:
        with conn:
            conn.execute(query)
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


def create_bookings_table(conn):
    query = """
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    try:
        with conn:
            conn.execute(query)
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
# Main wrapper function


def main():
    # Connect to the database
    conn = get_conn("travel.db")

    # Create the users table
    create_flights_table(conn)
    create_bookings_table(conn)


if __name__ == "__main__":
    main()  # Call the main function when the script is run directly
