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
    seller = str,
    authors=str,
    currency=str,
    cost_currency=int,
    cost_inr=int,
    total_cost=int,
    approval_remarks=str,
    current_stage=int,
    date_stage_update = datetime,
    pk='id',  # Primary key field (id will be automatically generated)
)

@app.get("/api/get-book-details")
async def get_book_details_api(isbn: str ):
    return functions.get_book_details(isbn)

@app.get("/")
def home(page: int = 1, sort_by: str = "date", order: str = "desc",search: str = "", date_range: str = "all"):
    return view.stage1(page, sort_by, order,search, date_range)

# Function to move the item to stage 2
@app.get("/move_to_stage2_from_stage1/{isbn}")
def move_to_stage2(isbn: int):
    functions.update_stage(isbn,1,2)
    return RedirectResponse("/stage2", status_code=302)

@app.get("/downloadentire")
def download_csv():
    return download.download_whole()

@app.get("/downloadstage1")
def download_csv():
    return download.download_stage1()

@app.post("/loadstage1")
async def restore_data(backup_file: UploadFile):
    functions.load(backup_file)
    return RedirectResponse("/", status_code=302)


@app.get("/stage2")
def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage2(page,sort_by,order,search,date_range)

@app.get("/downloadstage2")
def download_csv():
    return download.download_stage2()

@app.get("/move_to_stage1_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    functions.update_stage(isbn,2,1)
    return RedirectResponse("/", status_code=302)

@app.get("/move_to_stage3_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    functions.update_stage(isbn,2,3)
    return RedirectResponse("/stage3", status_code=302)

@app.get("/edit-book/{id}")
async def edit_book(id: int):
    res,js = await view.edit_in_stage2(id)
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm, Script(src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"), Script(js))

@app.post("/update-bookstage2")
def update_bookstage2(isbn: int, 
                      modified_isbn: int,
                      number_of_copies : int,
                      book_name: str, 
                      publisher: str,
                      seller: str, 
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
    """
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
                seller = ?, 
                authors = ?, 
                currency = ?, 
                cost_currency = ?, 
                cost_inr = ?, 
                total_cost = ?
            WHERE 
                isbn = ? AND 
                current_stage = 2
        """, (modified_isbn, number_of_copies, book_name, publisher,seller, authors, currency, cost_currency, cost_inr, total_cost, isbn))
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

@app.get("/downloadstage2")
def download_csv():
    return download.download_stage3()

@app.get("/move_to_stage4_from_stage3/{isbn}")
def move_to_stage4_from_stage3(isbn: int):
    functions.update_stage(isbn,3,4)
    
    return RedirectResponse("/stage4", status_code=302)
    

@app.get("/move_to_stage2_from_stage3/{isbn}")
def move_to_stage2_from_stage3(isbn: int):
    functions.update_stage(isbn,3,2)
    
    return RedirectResponse("/stage2", status_code=302)
    

@app.get("/edit-book_stage3/{id}")
async def edit_book(id: int):
    print(id)
    res = await view.edit_in_stage3(id)
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm)

@app.post("/update-bookstage3")
def update_bookstage3(isbn: int, 
                      number_of_copies : int, 
                      currency: str, 
                      cost_currency: float, 
                      cost_inr: float, 
                      status: str,
                      approval_remarks: str
                      ):
    
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    try:
        # Update the book details in the database
        cursor.execute("""
            UPDATE items
            SET  
                number_of_copies =?,  
                currency = ?, 
                cost_currency = ?, 
                cost_inr = ?, 
                status = ?,
                approval_remarks = ?
            WHERE 
                isbn = ? AND 
                current_stage = 3
        """, ( number_of_copies,  currency, cost_currency, cost_inr, status,approval_remarks, isbn))
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
