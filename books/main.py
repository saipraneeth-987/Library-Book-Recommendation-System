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
import fetch

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
    pk='id',  # Primary key field (id will be automatically generated)
)

@app.get("/api/get-book-details")
async def get_book_details_api(isbn: str ):
    return functions.get_book_details(isbn)


@app.get("/")
def home(page: int = 1, sort_by: str = "date", order: str = "desc",search: str = "", date_range: str = "all"):
    items_per_page = 10
    all_items = fetch_items_for_stage1()
    all_items = functions.filter_by_date(all_items, date_range)
    print(date_range)
    # Apply sorting only for 'date' and 'email' columns
    if sort_by in ["date", "email"]:
        reverse = order == "desc"
        column_index = {"date": 6, "email": 2}[sort_by]
        all_items.sort(key=lambda x: x[column_index], reverse=reverse)


    # Implement the search functionality
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    total_items = len(all_items)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Pagination logic
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_page_items = all_items[start_index:end_index]

    visible_pages = 5
    half_visible = visible_pages // 2
    start_page = max(1, page - half_visible)
    end_page = min(total_pages, page + half_visible)
    if page <= half_visible:
        end_page = min(total_pages, visible_pages)
    if page > total_pages - half_visible:
        start_page = max(1, total_pages - visible_pages + 1)

    pagination_controls = Div(
        *(
            [
                A("«", href=f"/?page={page - 1}&sort_by={sort_by}&order={order}&search={search}", style="margin-right: 10px;font-size: x-large;" + ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/?page={i}&sort_by={sort_by}&order={order}&search={search}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/?page={page + 1}&sort_by={sort_by}&order={order}&search={search}", style="margin-left: 10px;font-size: x-large;" + ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )

    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        # Set default order to "desc" if it's the first load (when order is not passed)
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(get_sort_icon(column), href=f"/?page={page}&sort_by={column}&order={new_order}&search={search}", style="text-decoration: none; font-size: small; margin-left: 5px;")

    date_range_options = Form(
        Group(
            Input(type="radio", name="date_range", value="all", id="all", checked=(date_range == "all"),onchange="this.form.submit()"),
            Label("All", for_="all", style="margin-right: 10px;"),
            Input(type="radio", name="date_range", value="1month", id="1month", checked=(date_range == "1month"),onchange="this.form.submit()"),
            Label("Last 1 Month", for_="1month", style="margin-right: 10px;"),
            Input(type="radio", name="date_range", value="3months", id="3months", checked=(date_range == "3months"),onchange="this.form.submit()"),
            Label("Last 3 Months", for_="3months", style="margin-right: 10px;"),
            Input(type="radio", name="date_range", value="6months", id="6months", checked=(date_range == "6months"),onchange="this.form.submit()"),
            Label("Last 6 Months", for_="6months"),
            style="margin-bottom: 20px; display: flex; align-items: center;"
        ),
        action="/", method="get"
    )

    table = Table(
        Tr(
            Th(Div("Date", create_sort_link("date"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th(Div("Email", create_sort_link("email"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Purpose", style="font-weight: 1000; text-align: center;"),
            Th("Remarks", style="font-weight: 1000; text-align: center;"),
            Th("Action", style=" font-weight: 1000;width: 110px; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px; maxwidth: 500px"),
                Td(A("Move to Stage 2", href=f"/move_to_stage2_from_stage1/{item[0]}", style="display:block;font-size: smaller; padding: 4px; width: 110px"))
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    search_box = Form(
        Group(
            Input(type="text", name="search", value=search, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/", method="get"
    )

    restore_form = Form(
        Group(
            Input(type="file", name="backup_file", accept=".csv", required=True, style="margin-right: 10px;"),
            Button("Restore", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/loadstage1", method="post", enctype="multipart/form-data"
    )

    card = Card(
        H3("Stage 1"),
        H6("This displays the details collected from googleform responses. It displays the order such that the latest book request on the top."),
        H6("Each book request is currently restored from Google Sheets CSV file. Initially, upload the CSV Google Sheet file and restore the details."),
        H6("Clicking 'Move to Stage 2' button sends the book request details to stage 2 from stage 1."),
        search_box,
        date_range_options,
        table,  
        pagination_controls,  # Display pagination controls
        header=Div(
            A("Stage 2", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 3", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 4", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 5", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 6", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Stage1", href="/downloadstage1", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            restore_form,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Book Recommendations', card)

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
def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= ""):
    items_per_page = 10

    # Fetch items for stage 2
    all_items = fetch_items_for_stage2()

    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date", "email"]:
        reverse = order == "desc"  # Set reverse based on 'desc' order
        column_index = {"date": 15, "email": 4}[sort_by]
        all_items.sort(key=lambda x: x[column_index], reverse=reverse)

    # Pagination calculations
    total_items = len(all_items)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    current_page_items = all_items[start_index:end_index]

    # Pagination controls
    visible_pages = 5
    half_visible = visible_pages // 2
    start_page = max(1, page - half_visible)
    end_page = min(total_pages, page + half_visible)

    if page <= half_visible:
        end_page = min(total_pages, visible_pages)
    if page > total_pages - half_visible:
        start_page = max(1, total_pages - visible_pages + 1)

    pagination_controls = Div(
        *(
            [
                A("«", href=f"/stage2?page={page - 1}&sort_by={sort_by}&order={order}", style="margin-right: 10px;font-size: x-large;" + ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage2?page={i}&sort_by={sort_by}&order={order}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage2?page={page + 1}&sort_by={sort_by}&order={order}", style="margin-left: 10px;font-size: x-large;" + ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )

    search_box = Form(
        Group(
            Input(type="text", name="search", value=search, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/stage2", method="get"
    )

    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        # Set default order to "desc" if it's the first load (when order is not passed)
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(get_sort_icon(column), href=f"/stage2?page={page}&sort_by={column}&order={new_order}", style="text-decoration: none; font-size: small; margin-left: 5px;")

    # Generate the table with sortable headers for "Date" and "Email"
    table = Table(
        Tr(
            Th("Id", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date", create_sort_link("date"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Modified_ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th(Div("Email", create_sort_link("email"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Name of Book", style="font-weight: 1000; text-align: center;"),
            Th("Remarks", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Seller", style="font-weight: 1000; text-align: center;"),
            Th("Author Names", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in INR", style="font-weight: 1000; text-align: center;"),
            Th("Total Cost", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;")
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller;"),
                Td(item[15], style="font-size: smaller;"),  # Date
                Td(item[1], style="font-size: smaller;"),   # ISBN
                Td(item[2], style="font-size: smaller;"),   # Modified ISBN
                Td(item[3], style="font-size: smaller;"),   # Recommender
                Td(item[4], style="font-size: smaller;"),   # Email
                Td(item[5], style="font-size: smaller;"),   # Number of Copies
                Td(item[6], style="font-size: smaller;"),   # Name of Book
                Td(item[7], style="font-size: smaller;"),   # Remarks
                Td(item[8], style="font-size: smaller;"),   # Publisher
                Td(item[9], style="font-size: smaller;"),
                Td(item[10], style="font-size: smaller;"),
                Td(item[11], style="font-size: smaller;"),
                Td(item[12], style="font-size: smaller;"),
                Td(item[13], style="font-size: smaller;"),
                Td(item[14], style="font-size: smaller;"),
                Td(
                    A("Edit", href=f"/edit-book/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Stage 3", href=f"/move_to_stage3_from_stage2/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Stage 1", href=f"/move_to_stage1_from_stage2/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}  # Add border to the table
    )

    # Card for displaying the book list in stage 2
    card = Card(
        H3("Stage 2"),  # Title for the list of books in stage 2
        H6("In this can edit the book details like the modified isbn and other . This can be done by collecting those details from the amazon,google etc "),
        H6("ISBN,Recommender,email,date all these are not editable and remaining are editable."),
        search_box,
        table,  # Display the table
        pagination_controls,  # Add pagination controls
        header=Div(
            A("Stage 1", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 3", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 4", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 5", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 6", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Stage2", href="/downloadstage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Stage 2 - Book Recommendations', card)

@app.get("/downloadstage2")
def download_csv():
    return download.download_stage2()

@app.get("/move_to_stage1_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    functions.update_stage(isbn,2,1)
    return RedirectResponse("/stage2", status_code=302)

@app.get("/move_to_stage3_from_stage2/{isbn}")
def move_to_stage2(isbn: int):
    functions.update_stage(isbn,2,3)
    return RedirectResponse("/stage2", status_code=302)

def fetch_items_for_stage1():
    return fetch.stage1()


def fetch_items_for_stage2():
    return fetch.stage2()

@app.get("/edit-book/{id}")
async def edit_book(id: int):
    
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage2', role="button", style="margin:15px"),
        
        # ISBN (non-editable)
        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1px solid #588C87"),  # Fetch ISBN from the stored data
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
            H6("Recommender", style="margin-right: 10px; min-width: 60px; text-align: left;color: #53B6AC;"),
            Input(id="recommender", readonly=True, style ="border:1px solid #588C87;"),  # Fetch recommender from stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("Email", style="margin-right: 10px; min-width: 60px; text-align: left;color: #53B6AC;"),
            Input(id="email", readonly=True, style ="border:1px solid #588C87;"),  # Fetch recommender from stored data
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

        Group(
            H6("seller", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="seller"),
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
       # Button("Save", role="button", style="margin-bottom: 15px;"),
       
        action="/update-bookstage2", id="edit", method='post'
    )
    
    # Fill the form with existing data
    frm = fill_form(res,BookRecommendations[id] )
    js = """
    async function load_book_details(){
        const isbn = document.getElementById('modified_isbn').value; 
        console.log('Modified ISBN:', isbn); 
    
        const authors = document.getElementById('authors'); 
        const title = document.getElementById('book_name');
        const publishers = document.getElementById('publisher');
        try {
            const response = await fetch(`/api/get-book-details?isbn=${isbn}`);
            console.log(response)
            if (response.ok) {
                const data = await response.json();
                console.log(data)
                if (data.error) {
                    authors.value = "Error: " + data.error;
                    title.value = "";
                    publishers.value = "";
                } else {
                    console.log("found")
                    console.log(data.authors)
                    authors.value = data.authors || "Unknown Authors";
                    console.log(authors.value)
                    title.value = data.title || "Unknown Title";
                    publishers.value = data.publishers || "Unknown Publishers";
                }
            } else {
                console.log("error in response");
                authors.value ="";
                title.value ="";
                publishers.value ="";
            }
        } catch (error) {
            authors.value ="";
            title.value ="";
            publishers.value ="";
        }
    };
    //window.onload = 
    load_book_details(); 
    document.getElementById('modified_isbn').oninput = load_book_details;
    """
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
