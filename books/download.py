from fasthtml.common import *
import csv
from io import StringIO
import sqlite3
import os
from fastapi.responses import StreamingResponse, RedirectResponse
import re

def download_whole():
    # Create an in-memory string buffer for CSV data
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date","status","modified_isbn","book_name","publisher","seller","authors","currency","cost_currency","cost_inr","total_cost","approval_remarks","stage"])

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
        headers={"Content-Disposition": "attachment; filename=booksdetails_stage1.csv"}
    )

def download_stage2():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    writer.writerow(["ID", "ISBN", "Recommender", "Email", "Number of Copies", "Purpose", "Remarks", "Date","modified_isbn","book_name","publisher","seller","authors","currency","cost_currency","cost_inr","total_cost"])

    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT id,isbn,recommender,email,number_of_copies,purpose,remarks,date,modified_isbn,book_name,publisher,seller,authors,currency,cost_currency,cost_inr,total_cost FROM items WHERE current_stage = 2")
    items = cursor.fetchall()

    for item in items:
        writer.writerow(item)

    connection.close()
    csv_file.seek(0)

    return StreamingResponse(
        csv_file,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=booksdetails_stage2.csv"}
    )

def download_stage3():
    csv_file = StringIO()
    writer = csv.writer(csv_file)

    # Write the header row for the CSV file
    writer.writerow(["ISBN", "Name of Book", "Number of Copies", "Currency", "Cost in Currency","Cost in INR","Status","Approval Remarks", "Recent Action Date"])

    # Connect to the SQLite database and fetch all items
    connection = sqlite3.connect('data/library.db')
    cursor = connection.cursor()
    cursor.execute("SELECT isbn,book_name, number_of_copies, currency,cost_currency,cost_inr,status,approval_remarks,date_stage_update FROM items WHERE current_stage = 3 ")
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
        headers={"Content-Disposition": "attachment; filename=booksdetails_stage3.csv"}
    )
