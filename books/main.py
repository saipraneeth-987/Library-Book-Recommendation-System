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
from flask import  request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


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
    await functions.load(backup_file)
    return RedirectResponse("/", status_code=302)


@app.get("/stage2")
def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage2(page,sort_by,order,search,date_range)

@app.get("/downloadstage2")
def download_csv():
    return download.download_stage2()

@app.get("/move_to_stage1_from_stage2/{isbn}")
def move_to_stage1_from_stage2(isbn: int):
    functions.update_stage(isbn,2,1)
    
    return RedirectResponse("/", status_code=302)


@app.get("/move_to_stage3_from_stage2/{isbn}")
def move_to_stage3_from_stage2(isbn: int):
    # Check if the book is fully updated with all mandatory fields
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    cursor.execute("""
        SELECT number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage2
        FROM items
        WHERE isbn = ? AND current_stage = 2
    """, (isbn,))
    
    result = cursor.fetchone()
    connection.close()
    
    if result:
        # Check for missing mandatory fields
        missing_fields = []
        number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage2 = result
        
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

        # If there are missing fields, return an error message
        if missing_fields:
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}
        
        # If all mandatory fields are filled, proceed to move to stage 3
        if availability_stage2 == "No":
            functions.update_stage(isbn, 2, 3)
            return RedirectResponse("/stage3", status_code=302)
        if availability_stage2 == "Yes":
            functions.update_stage(isbn, 2, 9)
            return RedirectResponse("/duplicate", status_code=302)
        
    
    return {"error": "No book found with the given ISBN in stage 2."}

@app.get("/edit-book/{id}")
async def edit_book(id: int):
    res,js = await view.edit_in_stage2(id)
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm, Script(src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"), Script(js))

@app.post("/update-bookstage2")
def update_bookstage2(
    isbn: int, 
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
        """, (modified_isbn, number_of_copies, book_name, sub_title, remarks_stage2, 
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



@app.get("/move_to_stage4_from_stage3/{isbn}")
def move_to_stage4_from_stage3(isbn: int):
    try:
        # Connect to the database
        connection = sqlite3.connect('data/library.db')
        cursor = connection.cursor()

        # Fetch the status of the item
        cursor.execute("""
            SELECT status
            FROM items
            WHERE isbn = ? AND current_stage = 3
        """, (isbn,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    if result:
        status = result[0]  # Extract the status from the query result

        # Handle status-based transitions
        if status == "approved":
            functions.update_stage(isbn, 3, 4)
            return RedirectResponse("/stage4", status_code=302)
        elif status == "rejected":
            functions.update_stage(isbn, 3, 10)
            return RedirectResponse("/notapproved", status_code=302)
        else:
            return {"error": f"Invalid status '{status}'. Only 'approved' or 'rejected' are valid."}
    else:
        return {"error": "No book found with the given ISBN in stage 3."}


@app.get("/move_to_stage2_from_stage3/{isbn}")
def move_to_stage2_from_stage3(isbn: int):
    functions.update_stage(isbn,3,2)
    return RedirectResponse("/stage2", status_code=302)
    

@app.get("/edit-book_stage3/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage3(id)
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage3")
def update_bookstage3(isbn: int,  
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

@app.get("/move_to_stage1_from_duplicate/{isbn}")
def move_to_stage1_from_duplicate(isbn: int):
    functions.update_stage(isbn,9,1)
    return RedirectResponse("/", status_code=302)

@app.get("/stage4")
def stage4(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage4(page,sort_by,order,search,date_range)

@app.get("/downloadstage4")
def download_csv():
    return download.download_stage4()

@app.get("/move_to_stage5_from_stage4/{isbn}")
def move_to_stage5_from_stage4(isbn: int):
    functions.update_stage(isbn,4,5)
    return RedirectResponse("/stage5", status_code=302)

@app.get("/move_to_stage3_from_stage4/{isbn}")
def move_to_stage3_from_stage4(isbn: int):
    functions.update_stage(isbn,4,3)
    return RedirectResponse("/stage3", status_code=302)



@app.get("/notapproved")  #stage 10
def notapproved(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.notapproved(page,sort_by,order,search,date_range)

@app.get("/downloadnotapproved")
def download_csv():
    return download.download_notapproved()

@app.get("/move_to_stage3_from_notapproved/{isbn}")
def move_to_stage1_from_notapproved(isbn: int):
    functions.update_stage(isbn,10,3)
    return RedirectResponse("/stage3", status_code=302)







@app.get("/stage5")
def stage5(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage5(page,sort_by,order,search,date_range)

@app.get("/downloadstage5")
def download_csv():
    return download.download_stage5()



@app.get("/move_to_stage6_from_stage5/{isbn}")
def move_to_stage6_from_stage5(isbn: int):
    try:
        # Connect to the database
        connection = sqlite3.connect('data/library.db')
        cursor = connection.cursor()

        # Fetch the status of the item
        cursor.execute("""
            SELECT availability_stage5
            FROM items
            WHERE isbn = ? AND current_stage = 5
        """, (isbn,))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        return {"error": f"Database error: {str(e)}"}
    finally:
        connection.close()

    if result:
        Availability = result[0].strip()  # Extract the status from the query result

        # Handle status-based transitions
        if Availability == "Available":
            functions.update_stage(isbn, 5, 6)
            return RedirectResponse("/stage6", status_code=302)
        elif Availability == "Not Available":
            functions.update_stage(isbn, 5, 11)
            return RedirectResponse("/stage11", status_code=302)
        else:
            return {"error": f"Invalid status '{Availability}'. Only 'Available' or 'Not Available' are valid."}
    else:
        return {"error": "No book found with the given ISBN in stage 5."}

@app.get("/move_to_stage4_from_stage5/{isbn}")
def move_to_stage4_from_stage5(isbn: int):
    functions.update_stage(isbn,5,4)
    return RedirectResponse("/stage4", status_code=302)
    

@app.get("/edit-book_stage5/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage5(id)
    frm = fill_form(res,BookRecommendations[id] )
    return Titled('Edit Book Recommendation', frm)


@app.post("/update-bookstage5")
def update_bookstage5(isbn: int,  
                      availability_stage5: str,
                      supplier_info:str,
                      remarks_stage5: str,
                      ):
    
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

@app.get("/move_to_stage5_from_stage11/{isbn}")
def move_to_stage5_from_stage11(isbn: int):
    functions.update_stage(isbn,11,5)
    return RedirectResponse("/stage5", status_code=302)
    

@app.get("/stage6")
def stage6(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage6(page,sort_by,order,search,date_range)

@app.get("/downloadstage6")
def download_csv():
    return download.download_stage6()


@app.get("/move_to_stage5_from_stage6/{isbn}")
def move_to_stage5_from_stage6(isbn: int):
    functions.update_stage(isbn,6,5)
    return RedirectResponse("/stage7", status_code=302)

@app.get("/edit-book_stage6/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage6(id)
    frm = fill_form(res,BookRecommendations[id] )
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

@app.get("/move_to_stage7_from_stage6/{isbn}")
def move_to_stage7_from_stage6(isbn: int):
    # Check if the book is fully updated with all mandatory fields
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()

    cursor.execute("""
        SELECT number_of_copies, book_name, publisher, edition_or_year, authors, currency, cost_currency,availability_stage5,supplier_info
        FROM items
        WHERE isbn = ? AND current_stage = 6
    """, (isbn,))
    
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
            return {"error": f"The following fields are mandatory and must be filled: {', '.join(missing_fields)}"}
        
        # If all mandatory fields are filled, proceed to move to stage 3
        if availability_stage5 == "Available":
            functions.update_stage(isbn, 6, 7)
            return RedirectResponse("/stage7", status_code=302)
        if availability_stage5 == "Not Available":
            functions.update_stage(isbn, 6, 11)
            return RedirectResponse("/stage11", status_code=302)
        
    
    return {"error": "No book found with the given ISBN in stage 6."}


@app.get("/stage7")
def stage7(page: int = 1, sort_by: str = "date_stage_update", order: str = "desc", search: str= "", date_range: str = "all"):
    return view.stage7(page,sort_by,order,search,date_range)

@app.get("/downloadstage7")
def download_csv():
    return download.download_stage7()


@app.get("/move_to_stage8_from_stage7/{isbn}")
def move_to_stage8_from_stage7(isbn: int):
    functions.update_stage(isbn,7,8)
    return RedirectResponse("/stage8", status_code=302)

@app.get("/move_to_stage6_from_stage7/{isbn}")
def move_to_stage6_from_stage7(isbn: int):
    functions.update_stage(isbn,7,6)
    return RedirectResponse("/stage6", status_code=302)


@app.get("/edit-book_stage7/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage7(id)
    frm = fill_form(res,BookRecommendations[id] )
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



@app.get("/move_to_stage7_from_stage8/{isbn}")
def move_to_stage6_from_stage7(isbn: int):
    functions.update_stage(isbn,8,7)
    return RedirectResponse("/stage7", status_code=302)


@app.get("/edit-book_stage8/{id}")
async def edit_book(id: int):
    res = await view.edit_in_stage8(id)
    frm = fill_form(res,BookRecommendations[id] )
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
        if len(mixed_row) < 2:
            raise HTTPException(status_code=400, detail="Please select more than one row.")
          
        print(f"Processing rows: {mixed_row}")  

        #combined_row = f"Combined: {row1} + {row2}"
        #print(f"Combined row: {combined_row}") 
        
        return {"message": f"Rows successfully clubbed"}

    except Exception as e:
        return JSONResponse(content={"message": f"Error clubbing rows: {str(e)}"}, status_code=500)

# Initialize the server
serve()
