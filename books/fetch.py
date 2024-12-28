import sqlite3
from datetime import datetime, timedelta

def stage1():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT isbn, recommender, email, number_of_copies, purpose, remarks, date
        FROM items
        WHERE current_stage = 1
        ORDER BY date DESC
    """)
    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    for idx, item in enumerate(items):
        date_str = item[6]  # The date is at index 6 in the tuple
        try:
            # If the date is not in ISO format, parse it and convert it to ISO format
            parsed_date = datetime.strptime(date_str, "%m.%d.%Y %H:%M:%S")
            items[idx] = item[:6] + (parsed_date.strftime("%Y-%m-%d %H:%M:%S"),) + item[7:]
        except ValueError:
            # Handle invalid date format if needed
            print(f"Invalid date format for {date_str} at index {idx}")

    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[6], reverse=True)

    return items

def stage2():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id,isbn, modified_isbn,recommender,email,number_of_copies,book_name,remarks,publisher,seller,authors,currency,cost_currency,cost_inr,total_cost,date
        FROM items
        WHERE current_stage = 2
        ORDER BY date DESC
    """)
    items = cursor.fetchall()
    connection.close()

    for idx, item in enumerate(items):
        date_str = item[15]  # The date is at index 6 in the tuple
        try:
            parsed_date = datetime.strptime(date_str, "%m.%d.%Y %H:%M:%S")
            items[idx] = item[:15] + (parsed_date.strftime("%Y-%m-%d %H:%M:%S"),) + item[15:]
        except ValueError:
            print(f"Invalid date format for {date_str} at index {idx}")

    items.sort(key=lambda x: x[15], reverse=True)

    return items

