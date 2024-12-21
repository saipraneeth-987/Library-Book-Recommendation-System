from fasthtml.common import *
import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
import re
from datetime import datetime

# Initialize the FastAPI application
app, rt, BookRecommendations, BookRecommendation = fast_app(
    'data/library.db',  # Path to your SQLite database
    id=int,  # Field type for the primary key
    isbn=int,  # ISBN of the book (should be string, not int)
    recommender=str,  # Name of the student or recommender
    email=str,  # Email of the person recommending the book
    number_of_copies=int,  # Number of copies recommended
    purpose=str,  # Purpose of the recommendation (e.g., Course, Reference)
    remarks=str,  # Remarks for the recommendation
    date=datetime,  # Date of recommendation
    status=str,  # Status of the recommendation
    modified_isbn=str,
    book_name=str,
    publisher=str,
    authors=str,
    currency=str,
    cost_currency=int,
    cost_inr=int,
    total_cost=int,
    approval_remarks=str,
    current_stage=int,
    pk='id',  # Primary key field (id will be automatically generated)
)

# Function to validate ISBN (either 10 or 13 digits)
def is_valid_isbn(isbn: str) -> bool:
    return bool(re.match(r'^\d{10}$', isbn)) or bool(re.match(r'^\d{13}$', isbn))

@app.get("/")
def home():
    # Fetch items from the database
    items = fetch_items_for_stage(1)
    # Generate a table with borders and a clear format
    table = Table(
        Tr(
            Th("ISBN"),
            Th("Recommender"),
            Th("Email"),
            Th("Number of Copies"),
            Th("Purpose"),
            Th("Remarks"),
            Th("Date"),
            
            Th("Action")
        ),
        *[
            Tr(
                Td(item[0]),
                Td(item[1]),
                Td(item[2]),
                Td(item[3]),
                Td(item[4]),
                Td(item[5]),
                Td(item[6]),
                
                Td(A("Move to Stage 2", href=f"/move_to_stage2/{item[0]}", role="button"))
            )
            for item in items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}  # Add border to the table
    )
    restore_form = Form(
        Group(
            Input(type="file", name="backup_file", accept=".csv", required=True, style="margin-right: 10px;"),
            Button("Restore", type="submit"),
            style="display: flex; align-items: center;"
        ),
        action="/restorestage1", method="post", enctype="multipart/form-data"
    )

    # Card for displaying the book list
    card = Card(
        H3("Recommended Books"),  # Title for the recommended books list
        table,  # Display the table
        header=Div(
            A("Download CSV", href="/downloadstage1", role="button", style="margin-left: 10px;"),  # Add download button
            #A("Restore", href="/restorestage1", role="button", style="margin-left: 10px;"),
            restore_form,
            A("Stage2", href="/stage2", role="button", style="margin-left: 10px;"),
            A("Stage3", href="/stage3", role="button", style="margin-left: 10px;"),
            A("Stage4", href="/stage4", role="button", style="margin-left: 10px;"),
            A("Stage5", href="/stage5", role="button", style="margin-left: 10px;"),
            A("Stage6", href="/stage6", role="button", style="margin-left: 10px;"),
            style="display: flex; gap: 10px;"  # Flexbox for layout  
        )
    )

    # Return the page with the table
    return Titled('Book Recommendations', card)


# Function to move the item to stage 2
@app.get("/move_to_stage2/{isbn}")
def move_to_stage2(isbn: int):
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Check if the book exists in stage 1
    cursor.execute("SELECT id FROM items WHERE isbn = ? AND current_stage = 1", (isbn,))
    book = cursor.fetchone()

    if book:
    # Update the item to stage 2
        cursor.execute("UPDATE items SET current_stage = 2 WHERE isbn = ? AND current_stage = 1", (isbn,))
        connection.commit()


    connection.close()

    return RedirectResponse("/stage2", status_code=302)


@app.get("/downloadstage1")
def download_csv():
    # Create an in-memory string buffer for CSV data
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date","stage"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id, isbn, recommender, email, number_of_copies, purpose, remarks, date ,current_stage FROM items ")
    items = cursor.fetchall()

    # Write each item to the CSV file
    for item in items:
        writer.writerow(item)

    # Close the database connection
    connection.close()

    # Reset the cursor to the beginning of the buffer
    csv_file.seek(0)

    # Return the CSV file as a streaming response for download
    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=booksstage1.csv"}
    )


@app.post("/restorestage1")
async def restore_data(backup_file: UploadFile):
    contents = await backup_file.read()
    contents = contents.decode("utf-8")  # Decode the uploaded file's content
    csv_reader = csv.reader(contents.splitlines())
    next(csv_reader, None)  # Skip the header row if it exists

    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Ensure the table exists with correct column definitions
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
        modified_isbn TEXT,
        book_name TEXT,
        publisher TEXT,
        authors TEXT,
        currency TEXT,
        cost_currency REAL,
        cost_inr REAL,
        total_cost REAL,
        approval_remarks TEXT,
        current_stage INTEGER NOT NULL DEFAULT 1, -- Tracks stage (1 to 6)
        UNIQUE(isbn, book_name, date) -- Ensure ISBN, Name, and date combination is unique
    )
    """)

    # Prepare the insert query
    insert_records = """
    INSERT OR IGNORE INTO items 
    (isbn, recommender, email, number_of_copies, purpose, remarks, date, current_stage) 
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """

    # Process each row in the CSV
    filtered_rows = []
    for row in csv_reader:
        # Extract and validate necessary fields
        
            isbn = row[3]  # Assuming ISBN is at the correct column index

            # Validate ISBN before proceeding
            if not is_valid_isbn(isbn):
                continue  # Skip invalid ISBNs completely

            # If the ISBN is valid, process the row and append to filtered_rows
            filtered_row = [isbn, row[18], row[1], row[5], row[4], row[6], row[0]]
            filtered_rows.append(filtered_row)


    # Insert the filtered data into the database
    cursor.executemany(insert_records, filtered_rows)

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    return RedirectResponse("/", status_code=302)


@app.get("/stage2")
def stage2():
    # Fetch items for stage 2
    items = fetch_items_for_stage(2)

    # Generate a table to display items in stage 2
    table = Table(
        Tr(
            Th("ISBN"),
            Th("Recommender"),
            Th("Email"),
            Th("Number of Copies"),
            Th("Purpose"),
            Th("Remarks"),
            Th("Date"),
            Th("Status")
        ),
        *[
            Tr(
                Td(item[0]),
                Td(item[1]),
                Td(item[2]),
                Td(item[3]),
                Td(item[4]),
                Td(item[5]),
                Td(item[6]),
                Td(item[7])
            )
            for item in items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}  # Add border to the table
    )

    # Card for displaying the book list in stage 2
    card = Card(
        H3("Books in Stage 2"),  # Title for the list of books in stage 2
        table,  # Display the table
        header=Div(
            A("Back to Stage 1", href="/", role="button", style="margin-left: 10px;"),
            A("Next Stage", href="/stage3", role="button", style="margin-left: 10px;"),
            style="display: flex; gap: 10px;"  # Flexbox for layout  
        )
    )

    # Return the page with the table of stage 2 items
    return Titled('Stage 2 - Book Recommendations', card)




def fetch_items_for_stage(stage: int):
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Fetch items from the database where current_stage matches the given stage, sorted by date in descending order
    cursor.execute("""
        SELECT isbn, recommender, email, number_of_copies, purpose, remarks, date, status 
        FROM items 
        WHERE current_stage = ?
        ORDER BY date DESC
    """, (stage,))

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
@app.get("/stage3")
def stage3():
    return "<h1>This is Stage3</h1>"

@app.get("/stage4")
def stage4():
    return "<h1>This is Stage4</h1>"

@app.get("/stage5")
def stage5():
    return "<h1>This is Stage5</h1>"

@app.get("/stage6")
def stage6():
    return "<h1>This is Stage6</h1>"

# Initialize the server
serve()
