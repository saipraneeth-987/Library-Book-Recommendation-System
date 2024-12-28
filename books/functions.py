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
        cursor.execute("SELECT id FROM items WHERE isbn = ? AND current_stage = ?", (isbn, current_stage))
        book= cursor.fetchone()
        if book:
            cursor.execute("UPDATE items SET current_stage = ? WHERE isbn = ? AND current_stage = ?",(new_stage, isbn, current_stage))
        connection.commit()

def get_book_details(isbn):
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        key = f"ISBN:{isbn}"
        if key in data:
            book = data[key]
            title = book.get("title", "Unknown Title")
            authors = ", ".join([author["name"] for author in book.get("authors", [])])
            publishers = ",".join([publisher["name"] for publisher in book.get("publishers",[])])
            print(book)
            return {"title": title, "authors": authors, "publishers": publishers}
        else:
            return {"error": "Book not found"}
    else:
        return {f"Failed to fetch details: {response.status_code}"}

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
        UNIQUE(isbn, recommender, date) -- Ensure ISBN, Name, and date combination is unique
    )
    """)

    insert_query = """
    INSERT OR IGNORE INTO items 
    (isbn, recommender, email, number_of_copies, purpose, remarks, date,modified_isbn, current_stage) 
    VALUES (?, ?, ?, ?, ?, ?, ?,?, 1)
    """

    check_query = """
    SELECT COUNT(*) FROM items WHERE isbn = ? AND recommender = ? AND date = ?
    """
    # Process each row in the CSV
    for row in csv_reader:
        try:
            # Extract necessary fields
            isbn = row[3]  # Assuming ISBN is at the correct column index
            recommender = row[18]  # Assuming recommender is at the correct column index
            email = row[1]  # Assuming email is at the correct column index
            number_of_copies = int(row[5])  # Assuming number of copies is at the correct column index
            purpose = row[4]  # Assuming purpose is at the correct column index
            remarks = row[6]  # Assuming remarks is at the correct column index
            date = row[0]  # Assuming date is at the correct column index


            # Check for duplicates
            cursor.execute(check_query, (isbn, recommender, date))
            count = cursor.fetchone()[0]
            if count > 0:
                continue  # Skip if duplicate found

            cursor.execute(insert_query, (isbn, recommender, email, number_of_copies, purpose, remarks, date,isbn))
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    connection.commit()
    connection.close()
