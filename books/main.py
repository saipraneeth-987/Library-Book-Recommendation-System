from fasthtml.common import *
import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
import re
from datetime import datetime, timedelta
import requests
import functions 
import download
import view
import fetch
from flask import  request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from flask import Flask, Response
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading
import asyncio

# Initialize the FastAPI application
app, rt, items, BookRecommendation = fast_app(
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
    sub_title = str,
    publisher=str,
    edition_or_year = str,
    authors=str,
    currency=str,
    cost_currency=float,
    cost_inr=float,
    total_cost=float,
    approval_remarks=str,
    seller = str,
    current_stage=int,
    date_stage_update = datetime,
    availability_stage2 = str,
    remarks_stage2 = str,
    availability_stage5 = str,
    supplier_info = str,
    remarks_stage5 = str,
    remarks_stage6 = str,
    remarks_stage7 = str,
    remarks_stage8 = str,
    clubbed = bool,
    c_id = list,
    pk='id',  # Primary key field (id will be automatically generated)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class RowData(BaseModel):
    mixedRow: list[str]

@app.get("/api/get-book-details")
async def get_book_details_api(isbn: str ):
    return functions.get_book_details(isbn)

@app.get("/api/fetch-gmail-name")
async def fetch_gmail_name_api(email: str):
    name = functions.fetch_name_from_gmail(email)  # Call your Gmail API fetching function
    return {"name": name}


@app.get("/")
def home(page: int = 1, sort_by: str = "date", order: str = "desc",search: str = "", date_range: str = "all"):
    return view.stage1(page, sort_by, order,search, date_range)

# Function to move the item to stage 2
@app.get("/move_to_stage2_from_stage1/{id}")
def move_to_stage2(id: int):
    functions.update_stage(id,1,2)
    return RedirectResponse("/stage2", status_code=302)

@app.get("/downloadentire")
def download_csv():
    return download.download_whole()

@app.get("/downloadstage1")
def download_csv():
    return download.download_stage1()

@app.post("/loadstage1")
async def restore_data(backup_file: UploadFile):
    await functions.load(backup_file)
    return RedirectResponse("/", status_code=302)


@app.get("/stage2")
def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage2(page,sort_by,order,search,date_range)

@app.get("/downloadstage2")
def download_csv():
    return download.download_stage2()

@app.get("/move_to_stage1_from_stage2/{id}")
def move_to_stage1_from_stage2(id: int):
    functions.update_stage(id,2,1)
    
    return RedirectResponse("/", status_code=302)


@app.get("/move_to_stage3_from_stage2/{id}")
def move_to_stage3_from_stage2(id: int):
    # Check if the book is fully updated with all mandatory fields
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    cursor.execute("""
        SELECT recommender,number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage2
        FROM items
        WHERE id = ? AND current_stage = 2
    """, (id,))
    
    result = cursor.fetchone()
    connection.close()
    
    if result:
        # Check for missing mandatory fields
        missing_fields = []
        recommender,number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage2 = result
        
        if not recommender:
            missing_fields.append("Recommender")
        if not number_of_copies:
            missing_fields.append("Number of copies")
        if not book_name:
            missing_fields.append("Title")
        if not publisher:
            missing_fields.append("Publisher")
        if not edition_or_year:
            missing_fields.append("Edition/Year")
        if not authors:
            missing_fields.append("Author")
        if not currency:
            missing_fields.append("Currency")
        if not cost_currency:
            missing_fields.append("Cost (in currency)")
        if not availability_stage2:
            missing_fields.append("Availability")

        # If there are missing fields, return an error message
        if missing_fields:
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}
        
        # If all mandatory fields are filled, proceed to move to stage 3
        if availability_stage2 == "No":
            functions.update_stage(id, 2, 3)
            return RedirectResponse("/stage3", status_code=302)
        if availability_stage2 == "Yes":
            functions.update_stage(id, 2, 9)
            return RedirectResponse("/duplicate", status_code=302)
        if availability_stage2 == "No Book found":
            functions.update_stage(id, 2, 9)
            return RedirectResponse("/duplicate", status_code=302)
        
    
    return {"error": "No book found with the given ISBN in stage 2."}

@app.get("/edit-book/{id}")
async def edit_book(id: int):
    # Get the form and the JavaScript code
    res, js = await view.edit_in_stage2(id)
    
    # Retrieve the book details to fill the form (assuming `items` contains your data)
    frm = fill_form(res, items[id])
    
    # Ensure the script for fetching book details and Gmail name is included
    return Titled(
        'Edit Book Recommendation',
        frm,
        Script(src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"),  # If needed
        Script(js)  # Include your custom JS to fetch book details and Gmail name
    )

@app.post("/update-bookstage2")
def update_bookstage2(
    isbn: int,
    recommender:str, 
    modified_isbn: int,
    number_of_copies: int,
    book_name: str, 
    sub_title: str,
    remarks_stage2: str,
    publisher: str,
    edition_or_year: str, 
    authors: str, 
    currency: str, 
    cost_currency: float,  
    availability_stage2: str
):
    
    
    # Check for missing mandatory fields
    missing_fields = []
    if not recommender:
        missing_fields.append("Recommender")
    if not number_of_copies:
        missing_fields.append("Number of copies")
    if not book_name:
        missing_fields.append("Title")
    if not publisher:
        missing_fields.append("Publisher")
    if not edition_or_year:
        missing_fields.append("Edition/Year")
    if not authors:
        missing_fields.append("Author")
    if not currency:
        missing_fields.append("Currency")
    if not cost_currency:
        missing_fields.append("Cost (in currency)")

    # Validate currency
    
    # Return error if any mandatory field is missing
    if missing_fields:
        return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

    # Connect to the database and update
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET 
                modified_isbn = ?, 
                recommender = ?,
                number_of_copies =?,
                book_name = ?, 
                sub_title =?,
                remarks_stage2=?,
                publisher = ?,
                edition_or_year = ?, 
                authors = ?, 
                currency = ?, 
                cost_currency = ?, 
                availability_stage2 = ?
            WHERE 
                isbn = ? AND 
                current_stage = 2
        """, (modified_isbn,recommender, number_of_copies, book_name, sub_title, remarks_stage2, 
              publisher, edition_or_year, authors, currency, cost_currency, availability_stage2, isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    return RedirectResponse(url="/stage2", status_code=302)

@app.get("/stage3")
def stage3(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage3(page,sort_by,order,search,date_range)

@app.get("/downloadstage3")
def download_csv():
    return download.download_stage3()



@app.get("/move_to_stage4_from_stage3/{id}")
def move_to_stage4_from_stage3(id: int):
    try:
        # Connect to the database
        connection = sqlite3.connect('data/library.db')
        cursor = connection.cursor()

        # Fetch the status of the item
        cursor.execute("""
            SELECT status
            FROM items
            WHERE id = ? AND current_stage = 3
        """, (id,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    if result:
        missing_fields = []
        status = result[0]  # Extract the status from the query result
        if not status:
            missing_fields.append("Status")
        if missing_fields:
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

        # Handle status-based transitions
        if status == "approved":
            functions.update_stage(id, 3, 4)
            return RedirectResponse("/stage4", status_code=302)
        elif status == "rejected":
            functions.update_stage(id, 3, 10)
            return RedirectResponse("/notapproved", status_code=302)
        else:
            return {"error": f"Invalid status '{status}'. Only 'approved' or 'rejected' are valid."}
    else:
        return {"error": "No book found with the given ISBN in stage 3."}


@app.get("/move_to_stage2_from_stage3/{id}")
def move_to_stage2_from_stage3(id: int):
    functions.update_stage(id,3,2)
    return RedirectResponse("/stage2", status_code=302)
    

@app.get("/edit-book_stage3/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage3(id)
    frm = fill_form(res,items[id] )
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage3")
def update_bookstage3(isbn: int,  
                      status: str,
                      approval_remarks: str
                      ):
    missing_fields = []
    if not status:
        missing_fields.append("Status")
    if missing_fields:
        return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET   
                status = ?,
                approval_remarks = ?
            WHERE 
                isbn = ? AND 
                current_stage = 3
        """, ( status,approval_remarks, isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    
    finally:
        connection.close()
    return RedirectResponse(url="/stage3", status_code=302)

@app.get("/duplicate")   # stage 9
def duplicate(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.duplicate(page,sort_by,order,search,date_range)

@app.get("/downloadduplicate")
def download_csv():
    return download.download_duplicate()

@app.get("/move_to_stage2_from_duplicate/{id}")
def move_to_stage2_from_duplicate(id: int):
    functions.update_stage(id,9,2)
    return RedirectResponse("/stage2", status_code=302)

@app.get("/stage4")
def stage4(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage4(page,sort_by,order,search,date_range)

@app.get("/downloadstage4")
def download_csv():
    return download.download_stage4()

@app.get("/move_to_stage5_from_stage4/{id}")
def move_to_stage5_from_stage4(id: int):
    functions.update_stage(id,4,5)
    return RedirectResponse("/stage5", status_code=302)

@app.get("/move_to_stage3_from_stage4/{id}")
def move_to_stage3_from_stage4(id: int):
    functions.update_stage(id,4,3)
    return RedirectResponse("/stage3", status_code=302)

@app.get("/notapproved")  #stage 10
def notapproved(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.notapproved(page,sort_by,order,search,date_range)

@app.get("/downloadnotapproved")
def download_csv():
    return download.download_notapproved()

@app.get("/move_to_stage3_from_notapproved/{id}")
def move_to_stage1_from_notapproved(id: int):
    functions.update_stage(id,10,3)
    return RedirectResponse("/stage3", status_code=302)


@app.get("/stage5")
def stage5(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage5(page,sort_by,order,search,date_range)

@app.get("/downloadstage5")
def download_csv():
    return download.download_stage5()


@app.get("/move_to_stage6_from_stage5/{id}")
def move_to_stage6_from_stage5(id: int):
    try:
        # Connect to the database
        connection = sqlite3.connect('data/library.db')
        cursor = connection.cursor()

        # Fetch the status of the item
        cursor.execute("""
            SELECT availability_stage5
            FROM items
            WHERE id= ? AND current_stage = 5
        """, (id,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    if result:
        Availability = result[0].strip()  # Extract the status from the query result
        missing_fields =[]
        if not Availability:
            missing_fields.append("Availability")
        if missing_fields:
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

        # Handle status-based transitions
        if Availability == "Available":
            functions.update_stage(id, 5, 6)
            return RedirectResponse("/stage6", status_code=302)
        elif Availability == "Not Available":
            functions.update_stage(id, 5, 11)
            return RedirectResponse("/stage11", status_code=302)
        else:
            return {"error": f"Invalid status '{Availability}'. Only 'Available' or 'Not Available' are valid."}
    else:
        return {"error": "No book found with the given ISBN in stage 5."}

@app.get("/move_to_stage4_from_stage5/{id}")
def move_to_stage4_from_stage5(id: int):
    functions.update_stage(id,5,4)
    return RedirectResponse("/stage4", status_code=302)
    

@app.get("/edit-book_stage5/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage5(id)
    frm = fill_form(res,items[id])
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage5")
def update_bookstage5(isbn: int,  
                      availability_stage5: str,
                      supplier_info:str,
                      remarks_stage5: str,
                      ):
    
    missing_fields = []
    if not availability_stage5:
        missing_fields.append("Availability")
    if not supplier_info:
        missing_fields.append("Supplier Information")
    if missing_fields:
        return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET   
                availability_stage5 = ?,
                supplier_info = ?,
                approval_remarks = ?
            WHERE 
                isbn = ? AND 
                current_stage = 5
        """, ( availability_stage5,supplier_info,remarks_stage5, isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    
    finally:
        connection.close()
    return RedirectResponse(url="/stage5", status_code=302)

@app.get("/stage11")
def stage11(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage11(page,sort_by,order,search,date_range)

@app.get("/downloadstage11")
def download_csv():
    return download.download_stage11()

@app.get("/move_to_stage5_from_stage11/{id}")
def move_to_stage5_from_stage11(id: int):
    functions.update_stage(id,11,5)
    return RedirectResponse("/stage5", status_code=302)

@app.get("/stage6")
def stage6(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage6(page,sort_by,order,search,date_range)

@app.get("/downloadstage6")
def download_csv():
    return download.download_stage6()


@app.get("/move_to_stage5_from_stage6/{id}")
def move_to_stage5_from_stage6(id: int):
    functions.update_stage(id,6,5)
    return RedirectResponse("/stage7", status_code=302)

@app.get("/edit-book_stage6/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage6(id)
    frm = fill_form(res,items[id])
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage6")
def update_bookstage6(
    modified_isbn: int,
    book_name: str, 
    sub_title: str,
    authors: str,
    publisher: str,
    edition_or_year: str,
    number_of_copies: int, 
    currency: str, 
    cost_currency: float,  
    availability_stage5: str,
    supplier_info:str,
    remarks_stage5:str,
    remarks_stage6:str,
):
    # Check for missing mandatory fields
    missing_fields = []
    if not book_name:
        missing_fields.append("Title")
    if not authors:
        missing_fields.append("Author")
    if not publisher:
        missing_fields.append("Publisher")
    if not edition_or_year:
        missing_fields.append("Edition/Year")
    if not number_of_copies:
        missing_fields.append("Number of copies")
    if not currency:
        missing_fields.append("Currency")
    if not cost_currency:
        missing_fields.append("Cost (in currency)")
    if not availability_stage5:
        missing_fields.append("Availability while Enquiry")
    if not supplier_info:
        missing_fields.append("Supplier Information")
    if missing_fields:
        return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}

    # Connect to the database and update
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET 
                modified_isbn = ?,
                book_name = ?,
                sub_title =?,
                authors = ?,
                publisher = ?,
                edition_or_year = ?,
                number_of_copies =?,
                currency = ?, 
                cost_currency = ?,
                availability_stage5 = ?,
                supplier_info = ?,
                remarks_stage5 = ?,
                remarks_stage6 = ?
            WHERE
                modified_isbn = ? AND
                current_stage = 6
        """, (modified_isbn,  book_name, sub_title,authors,
              publisher, edition_or_year,number_of_copies,  currency, cost_currency, availability_stage5,supplier_info,remarks_stage5,remarks_stage6, modified_isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {modified_isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    return RedirectResponse(url="/stage6", status_code=302)

@app.get("/move_to_stage7_from_stage6/{id}")
def move_to_stage7_from_stage6(id: int):
    # Check if the book is fully updated with all mandatory fields
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    cursor.execute("""
        SELECT number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage5,supplier_info
        FROM items
        WHERE id = ? AND current_stage = 6
    """, (id,))
    result = cursor.fetchone()
    connection.close()
    if result:
        # Check for missing mandatory fields
        missing_fields = []
        number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage5,supplier_info = result
        if not number_of_copies:
            missing_fields.append("Number of copies")
        if not book_name:
            missing_fields.append("Title")
        if not publisher:
            missing_fields.append("Publisher")
        if not edition_or_year:
            missing_fields.append("Edition/Year")
        if not authors:
            missing_fields.append("Author")
        if not currency:
            missing_fields.append("Currency")
        if not cost_currency:
            missing_fields.append("Cost (in currency)")
        if not availability_stage5:
            missing_fields.append("Availability while enquiry")
        if not supplier_info:
            missing_fields.append("Supplier Information")

        # If there are missing fields, return an error message
        if missing_fields:
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"
                    }
        # If all mandatory fields are filled, proceed to move to stage 3
        if availability_stage5 == "Available":
            functions.update_stage(id, 6, 7)
            return RedirectResponse("/stage7", status_code=302)
        if availability_stage5 == "Not Available":
            functions.update_stage(id, 6, 11)
            return RedirectResponse("/stage11", status_code=302)
    return {"error": "No book found with the given ISBN in stage 6."}


@app.get("/stage7")
def stage7(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage7(page,sort_by,order,search,date_range)

@app.get("/downloadstage7")
def download_csv():
    return download.download_stage7()

@app.get("/move_to_stage8_from_stage7/{id}")
def move_to_stage8_from_stage7(id: int):
    functions.update_stage(id,7,8)
    return RedirectResponse("/stage8", status_code=302)

@app.get("/move_to_stage6_from_stage7/{id}")
def move_to_stage6_from_stage7(id: int):
    functions.update_stage(id,7,6)
    return RedirectResponse("/stage6", status_code=302)


@app.get("/edit-book_stage7/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage7(id)
    frm = fill_form(res,items[id])
    return Titled('Edit Book Recommendation', frm)

@app.post("/update-bookstage7")
def update_bookstage7(isbn: int,  
                      remarks_stage7: str,
                      ):
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET
                remarks_stage7 = ?
            WHERE
                isbn = ? AND 
                current_stage = 7
        """, ( remarks_stage7, isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()
    return RedirectResponse(url="/stage7", status_code=302)

@app.get("/stage8")
def stage8(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage8(page,sort_by,order,search,date_range)

@app.get("/downloadstage8")
def download_csv():
    return download.download_stage8()

@app.get("/move_to_stage7_from_stage8/{id}")
def move_to_stage6_from_stage7(id: int):
    functions.update_stage(id,8,7)
    return RedirectResponse("/stage7", status_code=302)

@app.get("/edit-book_stage8/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage8(id)
    frm = fill_form(res,items[id])
    return Titled('Edit Book Recommendation', frm)

@app.post("/update-bookstage8")
def update_bookstage7(isbn: int,  
                      remarks_stage8: str,
                      ):
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET
                remarks_stage8 = ?
            WHERE 
                isbn = ? AND 
                current_stage = 8
        """, ( remarks_stage8, isbn))
        connection.commit()
        if cursor.rowcount == 0:
            return {"error": f"No book found with ISBN {isbn} to update."}
    except sqlite3.Error as e:
        # Rollback the transaction in case of error
        connection.rollback()
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()
    return RedirectResponse(url="/stage8", status_code=302)

@app.post("/club-rows")
async def club_rows(data: RowData):
    print(data.mixedRow)
    try:
        mixed_row = data.mixedRow
        if len(mixed_row) <= 1:
            raise HTTPException(status_code=400, detail="Please select more than one row.")
        else:
            with sqlite3.connect('data/library.db') as connection:
                cursor = connection.cursor()
                cursor.execute(""" select max(c_id) from items """)
                c_id = cursor.fetchone()[0]
                if c_id == 'None' or c_id == None:
                    c_id = 0
                c_id = int(c_id)
            for row in mixed_row:
                if "|" in row:
                    indices = row.split("|")
                    for index in indices:
                        id = int(index.strip())
                        book = items(where=f"id ={id}")[0]
                        book.clubbed = True
                        book.c_id = c_id+1
                        items.update(book)
                else:
                    id = int(row.strip())
                    book = items(where=f"id ={id}")[0]
                    book.clubbed = True
                    new_c_id = c_id+1
                    book.c_id = new_c_id
                    items.update(book)

            print(f"Processing rows: {mixed_row}")
        return {"message": f"Rows successfully clubbed"}

    except Exception as e:
        return JSONResponse(content={"message": f"Error clubbing rows: {str(e)}"}, status_code=500)

@app.get("/download_clubbed/{c_id}")
def download_clubbed(c_id: int):
    return download.clubbed(c_id)

@app.get("/edit_clubbed/{c_id}")
def edit_clubbed(c_id: int):
    return view.clubbed(c_id)

@app.get("/remove-club/{id}")
def remove_clubbed(id: int):
    print(id)
    book = items(where=f"id ={id}")[0]
    c_id = book.c_id
    same_cid_items = items(where=f"c_id ={c_id} and current_stage = 3")
    if (len(same_cid_items) == 2):
        other_book = items(where=f"c_id ={c_id} and current_stage = 3 and id != {id}")[0]
        other_book.clubbed = False
        other_book.c_id = None
        items.update(other_book)

    book.clubbed = False
    book.c_id = None
    items.update(book)

    return RedirectResponse("/stage3", status_code=302)

@app.get("/search")
def globalsearch(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search1: str= "", date_range: str = "all"):
    return view.globalsearch(page,sort_by,order,search1,date_range)


@app.get("/downloadsearch/{search}")
def download_csv(search: str):
    return download.download_search_data(search)

@app.get("/stage12")
def stage12(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage12(page,sort_by,order,search,date_range)

@app.get("/downloadstage12")
def download_csv():
    return download.download_stage12()

@app.get("/move_to_stage2_from_stage12/{id}")
def move_to_stage2_from_stage12(id: int):
    functions.update_stage(id,12,2)
    return RedirectResponse("/stage2", status_code=302)
@app.post("/approve_selected")
def approve_selected(data: RowData):
    print(data.mixedRow)
    try:
        mixed_row = data.mixedRow
        if len(mixed_row) < 1:
            raise HTTPException(status_code=400, detail="Please select atleast one row.")
        else:
            for row in mixed_row:
                id = int(row.strip())
                book = items(where=f"id ={id}")[0]
                book.status = "approved"
                items.update(book)
        return {"message": f"Rows successfully approved"}
    except Exception as e:
        return JSONResponse(content={"message": f"Error approving rows: {str(e)}"}, status_code=500)

@app.post("/move_selected")
def move_selected(data: RowData):
    print(data.mixedRow)
    try:
        mixed_row = data.mixedRow
        if len(mixed_row) < 1:
            raise HTTPException(status_code=400, detail="Please select atleast one row.")
        else:
            for row in mixed_row:
                id = int(row.strip())
                book = items(where=f"id ={id}")[0]
                status = book.status
                print(status)
                if status == "approved":
                    book.current_stage = 4
                    book.date_stage_update = datetime.now()
                    items.update(book)
                elif status == "rejected":
                    book.current_stage = 10
                    book.date_stage_update = datetime.now()
                    items.update(book)
                else:
                    return JSONResponse(content={"message": f"Update the status of {id} before moving."},status_code=400)
        return {"message": f"Rows successfully moved"}
    except Exception as e:
        return JSONResponse(content={"message": f"Error moving rows: {str(e)}"}, status_code=500)

@app.get("/duplicateRecommendation")
def initial_duplicates(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.duplicateRecommendation(page,sort_by,order,search,date_range)

@app.post("/backup")
async def backup_database():
    try:
    # Path to your database file
        db_file_path = "data/library.db"
        # Authenticate with Google Drive
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # This will prompt you to authenticate
        drive = GoogleDrive(gauth)

        # Upload the database file
        file_drive = drive.CreateFile({"title": "database_backup.db"})  # Set file name
        file_drive.SetContentFile(db_file_path)
        file_drive.Upload()
        return RedirectResponse("/", status_code=302)
    except Exception as e:
        return JSONResponse(
            {"error": str(e)}, status_code=500
        )

# Initialize the server
serve()
