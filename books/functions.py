import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi import UploadFile
import re
from datetime import datetime, timedelta
import requests

import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import pickle
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def fetch_name_from_gmail(email):
    """Fetch name associated with an email by searching Gmail."""
    creds = None

    # Load or authenticate credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\Lenovo\Downloads\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build Gmail service
    service = build('gmail', 'v1', credentials=creds)

    try:
        # Query to include only received and sent emails (From and To)
        query = f"from:{email} OR to:{email}"
        results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()

        if 'messages' not in results or not results['messages']:
            return f"No messages found for {email}"

        # Track the name for exact match
        name_found = None

        # Loop through messages to fetch exact name(s)
        for message in results['messages']:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            for header in headers:
                if header['name'] in ['From', 'To']:  # Only check From and To headers
                    sender = header['value']
                    match = re.match(r'(.*) <(.*)>', sender)
                    if match:
                        name, address = match.groups()
                        # Match exact email and return the name associated with it
                        if email.lower() == address.strip().lower():
                            name_found = name.strip()  # Store the name and stop further iterations
                            break
            if name_found:
                break  # Exit after finding the first match

        if name_found:
            return name_found
        else:
            return f"No name found for {email}"  # Return if no match is found

    except Exception as e:
        return f"An error occurred while fetching data for {email}: {e}"

def update_stage(id: int, current_stage: int,new_stage: int):
    with sqlite3.connect('data/library.db') as connection:
        cursor = connection.cursor()
        current_time = datetime.now()
        cursor.execute("SELECT id FROM items WHERE id = ? AND current_stage = ?", (id, current_stage))
        book= cursor.fetchone()
        if book:
            cursor.execute("UPDATE items SET current_stage = ?,date_stage_update = ? WHERE id = ? AND current_stage = ?",(new_stage,current_time, id, current_stage))
    
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


from datetime import datetime
import sqlite3
import csv
from fastapi import UploadFile

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
    (isbn, recommender, email, number_of_copies, purpose, remarks, date, current_stage, clubbed, c_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, 0)
    """

    check_query = """
    SELECT COUNT(*) FROM items WHERE isbn = ? AND recommender = ? AND email = ? AND number_of_copies = ? AND purpose = ? AND remarks = ? AND date = ?
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

            # Handle empty date by setting the current datetime
            if not date.strip():  # Check if date is empty or whitespace
                date = datetime.now().strftime("%m.%d.%Y %H:%M:%S")  # Use current datetime

            # Check for duplicates
            cursor.execute(check_query, (isbn, recommender, email, number_of_copies, purpose, remarks, date))
            count = cursor.fetchone()[0]
            if count > 0:
                continue  # Skip if duplicate found
            if not is_valid_isbn(isbn):
                continue

            # Insert the data into the database
            cursor.execute(insert_query, (isbn, recommender, email, number_of_copies, purpose, remarks, date))
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    connection.commit()
    connection.close()
