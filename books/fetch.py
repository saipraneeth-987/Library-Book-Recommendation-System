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
        SELECT id,isbn, modified_isbn,recommender,email,number_of_copies,book_name,sub_title,purpose,remarks_stage2,publisher,edition_or_year,authors,currency,cost_currency,date,availability_stage2
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
            items[idx] = item[:15] + (parsed_date.strftime("%Y-%m-%d %H:%M:%S"),) + item[16:]
        except ValueError:
            print(f"Invalid date format for {date_str} at index {idx}")

    items.sort(key=lambda x: x[15], reverse=True)

    return items

def stage3():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,clubbed,c_id
        FROM items
        WHERE current_stage = 3 and (clubbed = false or clubbed is null)
        ORDER BY date_stage_update DESC
    """)
    items = cursor.fetchall()
    cursor.execute("""
        SELECT GROUP_CONCAT(id, ' | '), GROUP_CONCAT(modified_isbn,' | '),GROUP_CONCAT( book_name, ' | '),GROUP_CONCAT( sub_title, ' | '),GROUP_CONCAT( authors, ' | '),GROUP_CONCAT( publisher, ' | '),GROUP_CONCAT( edition_or_year, ' | '), GROUP_CONCAT(  number_of_copies, ' | '),GROUP_CONCAT( currency, ' | '),GROUP_CONCAT( recommender, ' | '),GROUP_CONCAT( purpose, ' | '),GROUP_CONCAT( cost_currency, ' | '),GROUP_CONCAT( status, ' | '), GROUP_CONCAT(  approval_remarks, ' | '),GROUP_CONCAT( date_stage_update, ' | '),clubbed,c_id
        FROM items
        WHERE current_stage = 3 and clubbed = true
        group by c_id
        ORDER BY date_stage_update DESC
    """)
    clubbed_items = cursor.fetchall()
    connection.close()
    items = clubbed_items + items
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)
    return items

def duplicate():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id,isbn, modified_isbn,recommender,email,number_of_copies,book_name,sub_title,purpose,remarks_stage2,publisher,edition_or_year,authors,currency,cost_currency,date,availability_stage2
        FROM items
        WHERE current_stage = 9
        ORDER BY date DESC
    """)
    items = cursor.fetchall()
    connection.close()

    for idx, item in enumerate(items):
        date_str = item[15]  # The date is at index 6 in the tuple
        try:
            parsed_date = datetime.strptime(date_str, "%m.%d.%Y %H:%M:%S")
            items[idx] = item[:15] + (parsed_date.strftime("%Y-%m-%d %H:%M:%S"),) + item[16:]
        except ValueError:
            print(f"Invalid date format for {date_str} at index {idx}")

    items.sort(key=lambda x: x[15], reverse=True)

    return items

def stage4():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update
        FROM items
        WHERE current_stage = 4 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def notapproved():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update
        FROM items
        WHERE current_stage = 10 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def stage5():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,availability_stage5,supplier_info,remarks_stage5
        FROM items
        WHERE current_stage = 5 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def stage11():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id,modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,availability_stage5,supplier_info,remarks_stage5
        FROM items
        WHERE current_stage = 11 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def stage6():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,availability_stage5,supplier_info,remarks_stage5,remarks_stage6
        FROM items
        WHERE current_stage = 6 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def stage7():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,availability_stage5,supplier_info,remarks_stage5,remarks_stage6,remarks_stage7
        FROM items
        WHERE current_stage = 7 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items

def stage8():
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, modified_isbn, book_name, sub_title, authors, publisher, edition_or_year, 
            number_of_copies, currency, recommender, purpose, cost_currency, status, 
            approval_remarks, date_stage_update,availability_stage5,supplier_info,remarks_stage5,remarks_stage6,remarks_stage7,remarks_stage8
        FROM items
        WHERE current_stage = 8 
        ORDER BY date DESC
    """)

    items = cursor.fetchall()
    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    
    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14] if x[14] is not None else "", reverse=True)


    return items
