import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi import UploadFile
import re
from datetime import datetime, timedelta
import requests

def update_stage(isbn: int, current_stage: int,new_stage: int):
    with sqlite3.connect('data/library.db') as connection:
        cursor = connection.cursor()
        current_time = datetime.now()
        cursor.execute("SELECT id FROM items WHERE isbn = ? AND current_stage = ?", (isbn, current_stage))
        book= cursor.fetchone()
        if book:
            cursor.execute("UPDATE items SET current_stage = ?,date_stage_update = ? WHERE isbn = ? AND current_stage = ?",(new_stage,current_time, isbn, current_stage))
    
        connection.commit()

def get_book_details(isbn):
    if (isbn):
        api_key = "AIzaSyBVqOwuDKlY35_CSFSuhWzcAP4MIGnqLLU"
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{
            isbn}&key={api_key}"
        response = requests.get(url)
        url_openlib = f"https://openlibrary.org/api/books?bibkeys=ISBN:{
            isbn}&format=json&jscmd=data"
        response_openlib = requests.get(url_openlib)
        if response_openlib.status_code == 200:
            openlib_data = response_openlib.json()
            key = f"ISBN:{isbn}"
            print(openlib_data)
            if key in openlib_data:
                openlib_book = openlib_data[key]
                openlib_title = openlib_book.get("title", "Unknown Title")
                openlib_subtitle = openlib_book.get("subtitle", "")
                openlib_authors = ", ".join(
                    [author["name"] for author in
                     openlib_book.get("authors", [])])
                openlib_publishers = ",".join(
                    [publisher["name"] for publisher in
                     openlib_book.get("publishers", [])])
            else:
                openlib_data = None
        else:
            openlib_data = None
        if response.status_code == 200:
            data = response.json()
            print(data)
            if "items" in data:
                book = data["items"][0]["volumeInfo"]
                book = openlib_book if (
                    book == "" and openlib_data != None) else book
                title = book.get("title", "Unknown Title")
                title = openlib_title if (
                    title == "" and openlib_data != None) else title
                subtitle = book.get("subtitle", "")
                subtitle = openlib_subtitle if (
                    subtitle == "" and openlib_data != None) else subtitle
                authors = ", ".join(book.get("authors", ["Unknown Author"]))
                authors = openlib_authors if (
                    authors == "" and openlib_data != None) else authors
                publishers = book.get("publisher", ["Unknown Publisher"])
                publishers = openlib_publishers if (
                    publishers == "" and openlib_data != None) else publishers
                print("---------",title,subtitle,authors,publishers)
                return {"title": title,
                        "subtitle": subtitle,
                        "authors": authors,
                        "publishers": publishers}
            elif openlib_data is not None:
                return {"title": openlib_title,
                        "subtitle": openlib_subtitle,
                        "authors": openlib_authors,
                        "publishers": openlib_publishers}
            else:
                return {"error": "Book not found"}
        else:
            return {f"Failed to fetch details: {response.status_code}"}
    else:
        return {""}

def filter_by_date(all_items, date_range):
    today = datetime.today()
    if date_range == '1month':
        start_date = today - timedelta(days=30)
        print(start_date)
    elif date_range == '3months':
        start_date = today - timedelta(days=90)
    elif date_range == '6months':
        start_date = today - timedelta(days=180)
    else:
        return all_items  

    filtered_items = []
    for item in all_items:
        try:
            item_date = datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S")
            if item_date >= start_date:
                filtered_items.append(item)
        except Exception as e:
            print(f"Error parsing date for item: {item} - {e}")
            continue
    return filtered_items

def filter_by_date2(all_items, date_range):
    today = datetime.today()
    if date_range == '1month':
        start_date = today - timedelta(days=30)
        print(start_date)
    elif date_range == '3months':
        start_date = today - timedelta(days=90)
    elif date_range == '6months':
        start_date = today - timedelta(days=180)
    else:
        return all_items  

    filtered_items = []
    for item in all_items:
        try:
            item_date = datetime.strptime(item[15], "%Y-%m-%d %H:%M:%S")
            if item_date >= start_date:
                filtered_items.append(item)
        except Exception as e:
            print(f"Error parsing date for item: {item} - {e}")
            continue
    return filtered_items

def filter_by_date3(all_items, date_range):
    today = datetime.today()
    if date_range == '1month':
        start_date = today - timedelta(days=30)
        print(start_date)
    elif date_range == '3months':
        start_date = today - timedelta(days=90)
    elif date_range == '6months':
        start_date = today - timedelta(days=180)
    else:
        return all_items  

    filtered_items = []
    for item in all_items:
        try:
            item_date = datetime.strptime(item[14], "%Y-%m-%d %H:%M:%S.%f")
            if item_date >= start_date:
                filtered_items.append(item)
        except Exception as e:
            print(f"Error parsing date for item: {item} - {e}")
            continue
    return filtered_items

def filter_by_date_search(all_items, date_range):
    today = datetime.today()
    if date_range == '1month':
        start_date = today - timedelta(days=30)
        print(start_date)
    elif date_range == '3months':
        start_date = today - timedelta(days=90)
    elif date_range == '6months':
        start_date = today - timedelta(days=180)
    else:
        return all_items  

    filtered_items = []
    for item in all_items:
        try:
            item_date = datetime.strptime(item[6], "%Y-%m-%d %H:%M:%S.%f")
            if item_date >= start_date:
                filtered_items.append(item)
        except Exception as e:
            print(f"Error parsing date for item: {item} - {e}")
            continue
    return filtered_items

def is_valid_isbn(isbn: str) -> bool:
    return bool(re.match(r'^\d{10}$', isbn)) or bool(re.match(r'^\d{13}$', isbn))


async def load(backup_file: UploadFile):
    contents = await backup_file.read()
    contents = contents.decode("utf-8")  # Decode the uploaded file's content
    csv_reader = csv.reader(contents.splitlines())
    next(csv_reader, None)  # Skip the header row if it exists

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT NOT NULL,
        recommender TEXT NOT NULL,
        email TEXT NOT NULL,
        number_of_copies INTEGER NOT NULL,
        purpose TEXT NOT NULL,
        remarks TEXT,
        date DATETIME NOT NULL,
        status TEXT NOT NULL,
        modified_isbn INTEGER,
        book_name TEXT,
        publisher TEXT,
        seller TEXT,
        authors TEXT,
        currency TEXT,
        cost_currency REAL,
        cost_inr REAL,
        total_cost REAL,
        approval_remarks TEXT,
        current_stage INTEGER NOT NULL DEFAULT 1, -- Tracks stage (1 to 6)
        clubbed bool DEFAULT false,
        c_id text,
        UNIQUE(isbn, recommender, date) -- Ensure ISBN, Name, and date combination is unique
    )
    """)

    insert_query = """
    INSERT OR IGNORE INTO items 
    (isbn, recommender, email, number_of_copies, purpose, remarks, date, current_stage,clubbed,c_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, 1,0,0)
    """

    check_query = """
    SELECT COUNT(*) FROM items WHERE isbn = ? AND recommender = ? AND email = ? AND number_of_copies = ? AND purpose = ? AND remarks = ? AND date = ?
    """
    # Process each row in the CSV
    for row in csv_reader:
        try:
            # Extract necessary fields
            isbn = row[3]  # Assuming ISBN is at the correct column index
            if "-" in isbn:
                isbn = isbn.replace("-","")
            recommender = row[18]  # Assuming recommender is at the correct column index
            email = row[1]  # Assuming email is at the correct column index
            number_of_copies = int(row[5])  # Assuming number of copies is at the correct column index
            purpose = row[4]  # Assuming purpose is at the correct column index
            remarks = row[6]  # Assuming remarks is at the correct column index
            date = row[0]  # Assuming date is at the correct column index


            # Check for duplicates
            cursor.execute(check_query, (isbn, recommender,email,number_of_copies,purpose,remarks, date))
            count = cursor.fetchone()[0]
            if count > 0:
                continue  # Skip if duplicate found
            if not is_valid_isbn(isbn):
                continue
            cursor.execute(insert_query, (isbn, recommender, email, number_of_copies, purpose, remarks, date))
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue
    connection.commit()

    cursor.execute("""select id,isbn,number_of_copies from items where 
        isbn in (select isbn from items 
        group by isbn 
        having  count(isbn)>1
        order by count(isbn) desc) and current_stage = 1;""")
    duplicates_present = cursor.fetchall()
    max_copy_per_isbn = {}
    if duplicates_present:
        print(duplicates_present)
        for row in duplicates_present:
            print(row)
            id_,isbn,number_of_copies = row
            if isbn not in max_copy_per_isbn or number_of_copies > max_copy_per_isbn[isbn][2]:
                max_copy_per_isbn[isbn] = row
        max_tuples = list(max_copy_per_isbn.values())
        print(max_tuples)
        for row in duplicates_present:
            if row not in max_tuples:
                print(row)
                id_ = row[0]
                cursor.execute("""update items set current_stage = 12 where id = ?""",(id_,))
                connection.commit()
            connection.commit()
    connection.close()
