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
    book_name=int,
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
def is_valid_isbn(isbn: int) -> bool:
    return bool(re.match(r'^\d{10}$', isbn)) or bool(re.match(r'^\d{13}$', isbn))

@app.get("/")
def home():
    # Fetch items from the database
    items = fetch_items_for_stage1()
    # Generate a table with borders and a clear format
    table = Table(
        Tr(
            Th("Date"),
            Th("ISBN"),
            Th("Recommender"),
            Th("Email"),
            Th("Number of Copies"),
            Th("Purpose"),
            Th("Remarks"),
            Th("Action")
        ),
        *[
            Tr(
                Td(item[6]),
                Td(item[0]),
                Td(item[1]),
                Td(item[2]),
                Td(item[3]),
                Td(item[4]),
                Td(item[5]),
                Td(A("Move to Stage 2", href=f"/move_to_stage2_from_stage1/{item[0]}", role="button"))
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
        H3("Stage 1"),  # Title for the recommended books list
        H6("Each book requests are currently restored from googlesheets csv file"),
        H6("Initially upload the csv googlesheetfile and restore the details"),
        H6("This displays the isbn,name,email,number of copies etc details collected from googleform responses or requests. it displays the order such that the latest book request on the top."),
        H5("by clicking on the move to stage 2 the book request details goes to stage 2 from stage 1 andit wont appear in stage 1 "),
        H5("On the top different stages links are also provided can check the books present in each stage by just navigating to that satge "),
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
@app.get("/move_to_stage2_from_stage1/{isbn}")
def move_to_stage2(isbn: int):
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Check if the book exists in stage 2
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
    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date","status","modified_isbn","book_name","publisher","authors","currency","cost_currency","cost_inr","total_cost","approval_remarks","stage"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items ")
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
        modified_isbn INTEGER,
        book_name TEXT,
        publisher TEXT,
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

    # Prepare the insert query
    insert_query = """
    INSERT OR IGNORE INTO items 
    (isbn, recommender, email, number_of_copies, purpose, remarks, date, current_stage) 
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """

    # Prepare the select query to check for duplicates
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

            # Insert the row into the database
            cursor.execute(insert_query, (isbn, recommender, email, number_of_copies, purpose, remarks, date))
        except Exception as e:
            print(f"Error processing row {row}: {e}")
            continue

    # Commit changes and close the connection
    connection.commit()
    connection.close()

    return RedirectResponse("/", status_code=302)

@app.get("/stage2")
def stage2():
    # Fetch items for stage 2
    items = fetch_items_for_stage2()

    # Generate a table to display items in stage 2
    table = Table(
        Tr(
            Th("id"),
            Th("Date"),
            Th("ISBN"),
            Th("Modified_ISBN"),
            Th("Recommender"),
            Th("Email"),
            Th("Number of Copies"),
            Th("Name of Book"),
            Th("Remarks"),
            Th("Publisher"),
            Th("Author names"),
            Th("Currency"),
            Th("Cost in currency"),
            Th("Cost in INR"),
            Th("Total cost"),
            Th("Action")
        ),
        *[
            Tr(
                Td(item[0]),
                Td(item[14]),  # Date
                Td(item[1]),   # ISBN
                Td(item[2]),   # Modified ISBN
                Td(item[3]),   # Recommender
                Td(item[4]),   # Email
                Td(item[5]),   # Number of Copies
                Td(item[6]),   # Name of Book
                Td(item[7]),   # Remarks
                Td(item[8]),   # Publisher
                Td(item[9]),   # Author names
                Td(item[10]),   # Currency
                Td(item[11]),  # Cost in currency
                Td(item[12]),  # Cost in INR
                Td(item[13]),  # Total cost
                Td(
                    A("Edit", href=f"/edit-book/{item[0]}", role="button", style="margin-right: 10px;") ,
                    A("Move to Stage 3", href=f"/move_to_stage1_from_stage2/{item[1]}", role="button", style="margin-right: 10px;") ,
                    A("Move to Stage 1", href=f"/move_to_stage3_from_stage2/{item[1]}", role="button")
                )
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
@app.get("/move_to_stage1_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Check if the book exists in stage 2
    cursor.execute("SELECT id FROM items WHERE isbn = ? AND current_stage = 2", (isbn,))
    book = cursor.fetchone()

    if book:
    # Update the item to stage 2
        cursor.execute("UPDATE items SET current_stage = 1 WHERE isbn = ? AND current_stage = 2", (isbn,))
        connection.commit()


    connection.close()

    return RedirectResponse("/stage2", status_code=302)

@app.get("/move_to_stage3_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Check if the book exists in stage 2
    cursor.execute("SELECT id FROM items WHERE isbn = ? AND current_stage = 2", (isbn,))
    book = cursor.fetchone()

    if book:
    # Update the item to stage 2
        cursor.execute("UPDATE items SET current_stage = 3 WHERE isbn = ? AND current_stage = 2", (isbn,))
        connection.commit()


    connection.close()

    return RedirectResponse("/stage2", status_code=302)




def fetch_items_for_stage1():
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Fetch items from the database where current_stage matches the given stage, sorted by date in descending order
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


def fetch_items_for_stage2():
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    # Fetch items from the database where current_stage matches the given stage, sorted by date in descending order
    cursor.execute("""
        SELECT id,isbn, modified_isbn,recommender,email,number_of_copies,book_name,remarks,publisher,authors,currency,cost_currency,cost_inr,total_cost,date
        FROM items 
        WHERE current_stage = 2
        ORDER BY date DESC
    """)

    items = cursor.fetchall()

    connection.close()

    # Convert the date to proper datetime format and sort if necessary
    for idx, item in enumerate(items):
        date_str = item[14]  # The date is at index 6 in the tuple
        try:
            # If the date is not in ISO format, parse it and convert it to ISO format
            parsed_date = datetime.strptime(date_str, "%m.%d.%Y %H:%M:%S")
            items[idx] = item[:14] + (parsed_date.strftime("%Y-%m-%d %H:%M:%S"),) + item[14:]
        except ValueError:
            # Handle invalid date format if needed
            print(f"Invalid date format for {date_str} at index {idx}")

    # Sort by date in descending order after conversion
    items.sort(key=lambda x: x[14], reverse=True)

    return items

@app.get("/edit-book/{id}")
def edit_book(id: int):
    
    # Form creation with the fetched book details
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        
        # ISBN (non-editable)
        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="isbn", readonly=True),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Modified ISBN (editable)
        Group(
            H6("Modified ISBN", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="modified_isbn"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Name of recommender (non-editable)
        Group(
            H6("Recommender", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="recommender", readonly=True),  # Fetch recommender from stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Email", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="email", readonly=True),  # Fetch recommender from stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        # Number of copies (editable)
        Group(
            H6("Number of copies", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="number_of_copies", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Name of book (editable)
        Group(
            H6("Book Name", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="book_name"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Remarks (editable)
        Group(
            H6("Remarks", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="remarks"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Publisher (editable)
        Group(
            H6("Publisher", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="publisher"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Author names (editable)
        Group(
            H6("Author Names", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="authors"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Currency (editable)
        Group(
            H6("Currency", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="currency"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Cost in currency (editable)
        Group(
            H6("Cost (in Currency)", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="cost_currency", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Cost in INR (editable)
        Group(
            H6("Cost (in INR)", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="cost_inr", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Total cost (editable and auto-calculated)
        Group(
            H6("Total Cost", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="total_cost", type="number"),  # Read-only
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Actions: Save, Delete, Back
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/', role="button", style="margin:15px"),
        action="/update-bookstage2", id="edit", method='post'
    )
    
    # Fill the form with existing data
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage2")
def update_bookstage2(isbn: int, 
                      modified_isbn: int,
                      number_of_copies : int,
                      book_name: str, 
                      publisher: str, 
                      authors: str, 
                      currency: str, 
                      cost_currency: float, 
                      cost_inr: float, 
                      total_cost: float):
    """
    Updates the details of a book with the given ISBN in the database.

    Parameters:
    - isbn: int - The original ISBN of the book.
    - modified_isbn: str - The updated ISBN of the book.
    - book_name: str - The name of the book.
    - publisher: str - The publisher of the book.
    - authors: str - The authors of the book.
    - currency: str - The currency in which the cost is specified.
    - cost_currency: float - The cost in the specified currency.
    - cost_inr: float - The cost in INR.
    - total_cost: float - The total cost of the book.

    Returns:
    - JSON or RedirectResponse: Result of the operation.
    """
    # Connect to the SQLite database
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET 
                modified_isbn = ?, 
                number_of_copies =?,
                book_name = ?, 
                publisher = ?, 
                authors = ?, 
                currency = ?, 
                cost_currency = ?, 
                cost_inr = ?, 
                total_cost = ?
            WHERE 
                isbn = ? AND 
                current_stage = 2
        """, (modified_isbn, number_of_copies, book_name, publisher, authors, currency, cost_currency, cost_inr, total_cost, isbn))
        
        # Commit the transaction
        connection.commit()

        # Check if the update affected any rows
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    
    finally:
        # Close the database connection
        connection.close()

    # Redirect to the stage 2 page after a successful update
    return RedirectResponse(url="/stage2", status_code=302)

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


