from fasthtml.common import *
from datetime import datetime, timedelta
import fetch
import functions

items_per_page = 10

def stage1(page: int = 1, sort_by: str = "date", order: str = "desc",search: str = "", date_range: str = "all"):
    all_items = fetch.stage1()
    all_items = functions.filter_by_date(all_items, date_range,1)
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
                A("«", href=f"/?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                  ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-left: 10px;font-size: x-large;" +
                  ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )

    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"
    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
            style="text-decoration: none; font-size: small; margin-left: 5px;"
        )


    date_range_options = Form(
        Group(
            Input(type="hidden", name="search", value=search),
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
            Input(type="hidden", name="date_range", value=date_range), 
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

def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "",date_range:str ="all" ):
    items_per_page = 10
    all_items = fetch.stage2()
    all_items = functions.filter_by_date(all_items, date_range,2)
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

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
                A("«", href=f"/stage2?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}", style="margin-right: 10px;font-size: x-large;" + ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage2?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage2?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}", style="margin-left: 10px;font-size: x-large;" + ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )

    search_box = Form(
        Group(
            Input(type="hidden", name="date_range", value=date_range),
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
        new_order = "asc" if sort_by == column and order == "desc" else "desc"

        return A(
            get_sort_icon(column),
            href=f"/stage2?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
            style="text-decoration: none; font-size: small; margin-left: 5px;"
        )

    date_range_options = Form(
        Group(
            Input(type="hidden", name="search", value=search),
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
        action="/stage2", method="get"
    )

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
        date_range_options,
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

async def edit_in_stage2(id: int):
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
    return (res,js)

def stage3(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage3()
    all_items = functions.filter_by_date(all_items, date_range,3)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update", "date_stage2_completed"]:
        reverse = order == "desc"
        column_index = {
            "date_stage_update": 8,
            "date_stage2_completed": 8
        }.get(sort_by, 8)  # Default to index 8 if sort_by isn't found
        all_items.sort(key=lambda x: (x[column_index] is None, x[column_index]), reverse=reverse)

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
                A("«", href=f"/stage3?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage3?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage3?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-left: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )
    search_box = Form(
        Group(
            Input(type="text", name="search", value=search, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range),
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/stage3", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(get_sort_icon(column),
                 href=f"/stage3?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
                 style="text-decoration: none; font-size: small; margin-left: 5px;")
    date_range_options = Form(
        Group(
            Input(type="hidden", name="search", value=search),
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
        action="/stage3", method="get"
    )
    table = Table(
        Tr(
            Th(Div("ISBN", style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Name of Book", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in INR", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date Stage 2 Completed", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px; "),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage3/{item[9]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Stage 4", href=f"/move_to_stage4_from_stage3/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Stage 2", href=f"/move_to_stage2_from_stage3/{item[0]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
            if print(f"item[9]: {item[9]}") or True
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Stage 3"),
        H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Stage 1", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 2", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 4", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 5", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Stage 6", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Stage3", href="/downloadstage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Book Recommendations - Stage 3', card)

async def edit_in_stage3(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage3', role="button", style="margin:15px"),

        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1px solid #588C87"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Book Name", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="book_name", readonly=True, style ="border:1px solid #588C87"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("Number of copies", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="number_of_copies", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("currency", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="currency"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("cost in currency", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="cost_currency", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("Cost in INR", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="cost_inr", type="number"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("Status", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Select(
                Option("Select Status", value="", disabled=True, selected=True),
                Option("Approved", value="approved"),
                Option("Rejected", value="rejected"),
                id="status",
                style="padding: 5px; min-width: 120px;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Approval Remarks", style="margin-right: 10px; min-width: 60px; text-align: left;"),
            Input(id="approval_remarks"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        action="/update-bookstage3", id="edit", method='post'

    )
    return res
