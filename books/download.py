from fasthtml.common import *
import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
import re
import fetch
import functions
import view
import io
def download_whole():
    # Create an in-memory string buffer for CSV data
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date","status","modified_isbn","Title","Sub_Title","publisher","Edition/Year","author","currency","cost_currency","cost_inr","total_cost","approval_remarks","seller","current_stage","Recent Action Date","availability in Processing","Remarks while Processing","Remarks_Processing","Availability_Enquiry","Supplier Information","Remarks_Enquiry","Remarks after Ordered","Remarks After Received"])

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
        headers={"Content-Disposition": "attachment; filename=booksdetails_complete.csv"}
    )

def download_stage1():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,isbn,recommender,email,number_of_copies,purpose,remarks,date FROM items WHERE current_stage = 1 ")
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
        headers={"Content-Disposition": "attachment; filename=books_initiated.csv"}
    )

def download_stage2():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    writer.writerow(["ID", "ISBN","modified_isbn", "Recommender", "Email", "Number of Copies","Title","Sub Title" ,"Purpose", "Remarks","publisher","edition/year","author","currency","cost in currency", "Date","Book availability"])

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,isbn,modified_isbn,recommender,email,number_of_copies,book_name,sub_title,purpose,remarks_stage2,publisher,edition_or_year,authors,currency,cost_currency,date,availability_stage2 FROM items WHERE current_stage = 2")
    items = cursor.fetchall()

    for item in items:
        writer.writerow(item)

    connection.close()
    csv_file.seek(0)

    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_processing.csv"}
    )

def download_stage3():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,date_stage_update FROM items WHERE current_stage = 3  ")
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
        headers={"Content-Disposition": "attachment; filename=books_approval_pending.csv"}
    )


def download_duplicate():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    writer.writerow(["ID", "ISBN","modified_isbn", "Recommender", "Email", "Number of Copies","Title","Sub Title" ,"Purpose", "Remarks","publisher","edition/year","author","currency","cost in currency", "Date","Book availability"])

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,isbn,modified_isbn,recommender,email,number_of_copies,book_name,sub_title,purpose,remarks_stage2,publisher,edition_or_year,authors,currency,cost_currency,date,availability_stage2 FROM items WHERE current_stage = 9")
    items = cursor.fetchall()

    for item in items:
        writer.writerow(item)

    connection.close()
    csv_file.seek(0)

    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=books_duplicate.csv"}
    )


def download_stage4():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,date_stage_update FROM items WHERE current_stage = 3  ")
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
        headers={"Content-Disposition": "attachment; filename=books_approved.csv"}
    )

def download_notapproved():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,date_stage_update FROM items WHERE current_stage = 10  ")
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
        headers={"Content-Disposition": "attachment; filename=books_not_approved.csv"}
    )

def download_stage5():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks","Book Availability","supplier Information","Remarks while Enquiry", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,availability_stage5,supplier_info,remarks_stage5,date_stage_update FROM items WHERE current_stage = 5 ")
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
        headers={"Content-Disposition": "attachment; filename=books_under_enquiry.csv"}
    )

def download_stage11():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks","Book Availability","supplier Information","Remarks while Enquiry", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,availability_stage5,supplier_info,remarks_stage5,date_stage_update FROM items WHERE current_stage = 11 ")
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
        headers={"Content-Disposition": "attachment; filename=books_not_available.csv"}
    )

def download_stage6():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks","Book Availability","supplier Information","Remarks while Enquiry","Remarks while Ordering", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,availability_stage5,supplier_info,remarks_stage5,remarks_stage6,date_stage_update FROM items WHERE current_stage = 6 ")
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
        headers={"Content-Disposition": "attachment; filename=books_Ordered.csv"}
    )

def download_stage7():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks","Book Availability","supplier Information","Remarks while Enquiry","Remarks while Ordering","Remarks After Received", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,availability_stage5,supplier_info,remarks_stage5,remarks_stage6,remarks_stage7,date_stage_update FROM items WHERE current_stage = 7 ")
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
        headers={"Content-Disposition": "attachment; filename=books_Received.csv"}
    )

def clubbed(c_id):

    print(c_id)
    csv_file = StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(["ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Purpose of recommendation","Cost in Currency","Currency","Number of copies","Recommender","Date"])
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT isbn,book_name,sub_title,authors,publisher,edition_or_year,purpose,cost_currency,currency,number_of_copies,recommender,date FROM items WHERE current_stage = 3 and c_id = ?", (c_id,))
    items = cursor.fetchall()
    for item in items:
        writer.writerow(item)
        
    connection.close()
    csv_file.seek(0)
    return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=clubbed.csv"}
        )
    
def download_stage8():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID","ISBN", "Title", "Sub Title", "Author","Publisher","Edition/year","Number of copies","Currency", "Recommender","Purpose of recommendation","Cost in Currency","Status","Approval Remarks","Book Availability","supplier Information","Remarks while Enquiry","Remarks while Ordering","Remarks After Received","Remarks After Processed", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,modified_isbn,book_name,sub_title,authors,publisher,edition_or_year, number_of_copies, currency,recommender,purpose,cost_currency,status,approval_remarks,availability_stage5,supplier_info,remarks_stage5,remarks_stage6,remarks_stage7,remarks_stage8,date_stage_update FROM items WHERE current_stage = 8 ")
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
        headers={"Content-Disposition": "attachment; filename=books_Processed.csv"}
    )



def download_search_data(search: str = view.search1, date_range: str = "all", sort_by: str = "date", order: str = "desc", items_per_page: int = 10):
    # Fetch and filter data as done in the globalsearch function
    all_items = fetch.allstage()

    # Filter by date range
    all_items = functions.filter_by_date(all_items, date_range)

    # If search is provided, filter by the search term
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]
    
    # Sorting based on the 'sort_by' and 'order' parameters
    if sort_by in ["date_stage_update", "email"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 6, "email": 3}[sort_by]
        all_items.sort(key=lambda x: x[column_index] if x[column_index] is not None else "", reverse=reverse)

    # Prepare CSV data
    output = StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(["ISBN", "Modified_ISBN", "Recommender", "Email", "Title", "Current Stage", "Recent Action Date"])
    stage_mapping = {
        1: "Initiated",
        2: "Processing",
        3: "Approval Pending",
        4: "Approved",
        5: "Under Enquiry",
        6: "Ordered",
        7: "Received",
        8: "Processed",
        9: "Duplicate",
        10: "Not Approved",
        11: "Not Available"
    }

    # Write rows for the filtered and sorted data
    for item in all_items:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], stage_mapping.get(item[5], "Unknown"), item[6]])

    # Get the CSV data as a string
    output.seek(0)
    output_str = output.getvalue()

    # Return CSV file as downloadable response
    return Response(
        output_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=filtered_data.csv"}
    )
