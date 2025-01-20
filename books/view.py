from fasthtml.common import *
from datetime import datetime, timedelta
import fetch
import functions


items_per_page: int = 10
search1:str=""

def stage1(page: int = 1, sort_by: str = "date", order: str = "desc", search: str = "", date_range: str = "all", items_per_page: int = 10):
    # Fetch items and apply filters
    all_items = fetch.stage1()
    all_items = functions.filter_by_date(all_items, date_range)
    # Apply sorting only for 'date' and 'email' columns
    if sort_by in ["date", "email"]:
        reverse = order == "desc"
        column_index = {"date": 6, "email": 2}[sort_by]
        all_items.sort(key=lambda x: x[column_index], reverse=reverse)
    all_stages = fetch.allstage()
    if search1:
        search_lower = search.lower()
        all_items = [
            item for item in all_stages
            if any(search_lower in str(value).lower() for value in item)
        ]
    # Implement the search functionality
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]
    # Total items and pagination
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

    # Pagination controls
    pagination_controls = Div(
        *(
            [
                A("«", href=f"/?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
                  style="margin-right: 10px;font-size: x-large;" +
                  ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
                  style="margin-left: 10px;font-size: x-large;" +
                  ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
            ]
        ),
        style="margin-top: 10px; text-align: center;"
    )

    # Dropdown for items per page
    items_per_page_buttons = Div(
        A("20", href=f"/?page=1&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page=20",
           style="margin-right: 10px; font-size: large;"),
        A("50", href=f"/?page=1&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page=50",
           style="margin-right: 10px; font-size: large;"),
        A("100", href=f"/?page=1&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page=100",
           style="font-size: large;"),
        style="text-align: center; margin-bottom: 20px;"
    )

    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"
    
    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
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
                Td(A("Move to next Stage ", href=f"/move_to_stage2_from_stage1/{item[0]}", style="display:block;font-size: smaller; padding: 4px; width: 110px"))
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

    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
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
        H3("Stage 1 - Initiated phase"),
        H6("This displays the details collected from googleform responses. It displays the order such that the latest book request on the top."),
        H6("Each book request is currently restored from Google Sheets CSV file. Initially, upload the CSV Google Sheet file and restore the details."),
        H6("Clicking 'Move to Stage 2' button sends the book request details to stage 2 from stage 1."),
        search_box,
        date_range_options,
        items_per_page_buttons,  # Display the items per page buttons
        table,  
        pagination_controls,  # Display pagination controls
        header=Div(
            #A("Globalsearch", href="/search", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Initiated books", href="/downloadstage1", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            restore_form,
            global_search_box,
            style="display: flex; align-items: center; justify-content: flex-start; padding: 20px; height: 50px; font-weight: 700;"
        ),
    )
    return Titled('Books Initiated', card)

def stage2(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    
    all_items = fetch.stage2()
    all_items = functions.filter_by_date2(all_items, date_range)
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
                A("«", href=f"/stage2?page={page - 1}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}", style="margin-right: 10px;font-size: x-large;" + ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage2?page={i}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage2?page={page + 1}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}", style="margin-left: 10px;font-size: x-large;" + ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
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
        action="/stage2", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"
    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"

        return A(
            get_sort_icon(column),
            href=f"/stage2?page={page}&sort_by={column}&order={new_order}&search={search}date_range={date_range}",
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
            Th("ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Modified_ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th(Div("Email", create_sort_link("email"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub-Title", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of Recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Remarks", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date", create_sort_link("date"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Availability", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;")
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller;"),
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
                Td(item[15], style="font-size: smaller;"),  # Date
                Td(item[16], style="font-size: smaller;"),  
                Td(
                    A("Edit", href=f"/edit-book/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage3_from_stage2/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage1_from_stage2/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}  # Add border to the table
    )

    # Card for displaying the book list in stage 2
    card = Card(
        H3("Books Processing"),  # Title for the list of books in stage 2
        H6("In this can edit the book details like the modified isbn and other . This can be done by collecting those details from the amazon,google etc "),
        H6("ISBN,Recommender,email,date all these are not editable and remaining are editable."),
        search_box,
        date_range_options,
        table,  # Display the table
        pagination_controls,  # Add pagination controls
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Stage2", href="/downloadstage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Stage 2 - Books Processing', card)
async def edit_in_stage2(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage2', role="button", style="margin:15px"),

        # ISBN (non-editable)
        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC;"),
            Input(id="isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Modified ISBN (editable)
        Group(
            H6("Modified ISBN (*)", style="margin-right: 10px; color: #D369A3; min-width: 60px; text-align: left;"),
            Input(id="modified_isbn", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Name of recommender (non-editable)
        Group(
            H6("Recommender", style="margin-right: 10px; min-width: 60px; text-align: left;color: #53B6AC;"),
            Input(id="recommender", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch recommender from stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        Group(
            H6("Email", style="margin-right: 10px; min-width: 60px; text-align: left;color: #53B6AC;"),
            Input(id="email", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch recommender from stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        # Number of copies (editable)
        Group(
            H6("Number of copies", style="margin-right: 10px; color: #D369A3; min-width: 60px; text-align: left;"),
            Input(id="number_of_copies", type="number", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Name of book (editable)
        Group(
            H6("Title(*)", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="book_name", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Sub Title", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="sub_title", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),


        # Remarks (editable)
        Group(
            H6("Remarks", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage2", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Publisher (editable)
        Group(
            H6("Publisher(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="publisher", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Edition/Year(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="edition_or_year", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Author names (editable)
        Group(
            H6("Author(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="authors", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Currency (editable)
        Group(
            H6("Currency(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Select(
                Option("Select Currency", value="", disabled=True, selected=True), #"USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD"
                Option("USD", value="USD"),
                Option("EUR", value= "EUR"),
                Option("JPY", value= "JPY" ),
                Option("GBP" , value="GBP" ),
                Option("AUD", value="AUD" ),
                Option("CHF" , value="CHF" ),
                Option("CAD" , value= "CAD"),
                Option("CNY", value="CNY" ),
                Option("SEK" , value="SEK" ),
                Option("NZD" , value="NZD" ),
                id="currency",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Cost in currency (editable)
        Group(
            H6("Cost in Currency(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="cost_currency", type="float", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        
        # Total cost (editable and auto-calculated)
        Group(
            H6("Book Availability", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Select(
                Option("Select Availability", value="", disabled=True, selected=True),
                Option("Yes", value="Yes"),
                Option("No", value="No"),
                id="availability_stage2",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
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
        const subtitle = document.getElementById('sub_title');
        const publishers = document.getElementById('publisher');
        try {
            const response = await fetch(`/api/get-book-details?isbn=${isbn}`);
            console.log(response)
            if (response.ok) {
                const data = await response.json();
                console.log(data)
                if (data.error) {
                    authors.value = "Error: " + data.error;
                    subtitle.value = "";
                    title.value = "";
                    publishers.value = "";
                } else {
                    console.log("found")
                    console.log(data.authors)
                    authors.value = data.authors || "Unknown Authors";
                    console.log(authors.value)
                    subtitle.value = data.subtitle;
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


def stage3(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc",search: str ="",date_range:str="all"):
    all_items = fetch.stage3()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
        all_items.sort(
            key=lambda x: (x[column_index] is None, x[column_index] if x[column_index] is not None else ""), 
            reverse=reverse
        )

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
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage3?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage3", method="get"
    )
    table = Table(
        Tr(
            Th("Select", style="font-weight: 1000; text-align: center;"),
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                #id=f"row-{item[0]}",
                #content = [
                Td(
                Input(type="checkbox", name="row_checkbox", value=item[0], style="margin: auto;"),  # Checkbox in each row
                style="text-align: center; padding: 4px;"
            ),
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td((
                    A("Edit", href=f"/edit-book_stage3/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage4_from_stage3/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage2_from_stage3/{item[1]}", style="display:block;font-size: smaller;")) if item[15]==0 else (
                    A("Download", href=f"/download_clubbed/{item[16]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Edit", href=f"/edit_clubbed/{item[16]}",style="display:block;font-size: smaller;margin-bottom:3px")
                    )
                   )
                )
            for item in current_page_items
        ],
        id = "book-table",
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Stage 3"),
        H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        Button("Club Rows", id="club-rows-button", style="margin-top: 10px; ",action ="/club-rows",method = "post"),
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download approval pending books", href="/downloadstage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    js = """
        document.getElementById('club-rows-button').onclick = function () {
        const selectedRows = Array.from(document.querySelectorAll('input[name="row_checkbox"]:checked')).map(cb => cb.value);
        console.log(selectedRows)
        if (selectedRows.length > 1) {
            fetch('http://localhost:5001/club-rows', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mixedRow: selectedRows })
            })
                .then(response => {
                    console.log(response)
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Rows clubbed successfully:', data);
                    console.log(data);
                    document.querySelectorAll('input[name="row_checkbox"]:checked').forEach(cb => cb.checked = false);
                    setTimeout(() => location.reload(), 100);
                })
                .catch(error => {
                    console.error('Error clubbing rows:', error);
                    alert('Error clubbing rows: ' + error.message);
                });
        } else {
            alert('Please select more than one row to club.');
        }
    };
    """
    return (Titled('Book Recommendations - Stage 3', card),Script(src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"), Script(js))

async def edit_in_stage3(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage3', role="button", style="margin:15px"),

        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        Group(
            H6("Status", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Select(
                Option("Select Status", value="", disabled=True, selected=True),
                Option("Approved", value="approved"),
                Option("Rejected", value="rejected"),
                id="status",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Approval Remarks", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="approval_remarks" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        action="/update-bookstage3", id="edit", method='post'

    )
    return res


def duplicate(page: int = 1, sort_by: str = "date", order: str = "desc", search: str= "", date_range: str = "all"):
    all_items = fetch.duplicate()
    all_items = functions.filter_by_date2(all_items, date_range)
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
                A("«", href=f"/duplicate?page={page - 1}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}", style="margin-right: 10px;font-size: x-large;" + ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/duplicate?page={i}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/duplicate?page={page + 1}&sort_by={sort_by}&order={order}&search={search}date_range={date_range}", style="margin-left: 10px;font-size: x-large;" + ("visibility: hidden;" if page == total_pages else "visibility: visible;"))
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
        action="/duplicate", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )

    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"
    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"

        return A(
            get_sort_icon(column),
            href=f"/duplicate?page={page}&sort_by={column}&order={new_order}&search={search}date_range={date_range}",
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
            Th("ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Modified_ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th(Div("Email", create_sort_link("email"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub-Title", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of Recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Remarks", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date", create_sort_link("date"), style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Availability", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;")
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller;"),
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
                Td(item[15], style="font-size: smaller;"),  # Date
                Td(item[16], style="font-size: smaller;"),  
                Td(
                    A("Move to Initial  Stage ", href=f"/move_to_stage1_from_duplicate/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}  # Add border to the table
    )

    # Card for displaying the book list in stage 2
    card = Card(
        H3("Duplicate Books "),  # Title for the list of books in stage 2
        search_box,
        date_range_options,
        table,  # Display the table
        pagination_controls,  # Add pagination controls
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download duplicates", href="/downloadduplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled(' Duplicate Books ', card)

def stage4(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage4()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage4?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage4?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage4?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage4", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage4?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage4", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
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
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Move to Next Stage ", href=f"/move_to_stage5_from_stage4/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage3_from_stage4/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books Approved"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Approved books", href="/downloadstage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Approved', card)

def notapproved(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.notapproved()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/notapproved?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/notapproved?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/notapproved?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/notapproved", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/notapproved?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/notapproved", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
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
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Move to Previous Stage ", href=f"/move_to_stage3_from_notapproved/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books not  Approved"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download Approved books", href="/downloadnotapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books not Approved', card)

def stage5(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage5()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage5?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage5?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage5?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage5", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage5?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage5", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Book Available", style="font-weight: 1000; text-align: center;"),
            Th("Supplier Information", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Enquiry", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;"),
                Td(item[15], style="font-size: smaller; padding: 4px;"),
                Td(item[16], style="font-size: smaller; padding: 4px;"),
                Td(item[17], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage5/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage6_from_stage5/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage4_from_stage5/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books Under Enquiry"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download books here", href="/downloadstage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Under Enquiry', card)


async def edit_in_stage5(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage5', role="button", style="margin:15px"),

        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        Group(
            H6("Book Available", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Select(
                Option("Select Availability", value="", disabled=True, selected=True),
                Option("Available", value="Available"),
                Option("Not Available", value="Not Available"),
                id="availability_stage5",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Supplier Information(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="supplier_info", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Remarks while enquiry", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage5" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        action="/update-bookstage5", id="edit", method='post'

    )
    return res

def stage11(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage11()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage11?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage11?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage11?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage11", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage11?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage11", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Book Available", style="font-weight: 1000; text-align: center;"),
            Th("Supplier Information", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Enquiry", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;"),
                Td(item[15], style="font-size: smaller; padding: 4px;"),
                Td(item[16], style="font-size: smaller; padding: 4px;"),
                Td(item[17], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Move to Previous Stage ", href=f"/move_to_stage5_from_stage11/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books not Available after Enquiry"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books Under Enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download books here", href="/downloadstage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Not Available', card)

def stage6(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage6()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage6?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage6?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage6?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage6", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage6?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage6", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Book Available", style="font-weight: 1000; text-align: center;"),
            Th("Supplier Information", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Enquiry", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Ordering", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;"),
                Td(item[15], style="font-size: smaller; padding: 4px;"),
                Td(item[16], style="font-size: smaller; padding: 4px;"),
                Td(item[17], style="font-size: smaller; padding: 4px;"),
                Td(item[18], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage6/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage7_from_stage6/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage5_from_stage6/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books  Ordered"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under Enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download books here", href="/downloadstage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Ordered', card)

async def edit_in_stage6(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage6', role="button", style="margin:15px"),

        # ISBN (non-editable)
        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC;"),
            Input(id="modified_isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),

        

        # Name of book (editable)
        Group(
            H6("Title(*)", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="book_name", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Sub Title", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="sub_title", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Author names (editable)
        Group(
            H6("Author(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="authors", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),


        # Publisher (editable)
        Group(
            H6("Publisher(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="publisher", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Edition/Year(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="edition_or_year", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Number of copies (editable)
        Group(
            H6("Number of copies", style="margin-right: 10px; color: #D369A3; min-width: 60px; text-align: left;"),
            Input(id="number_of_copies", type="number", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        # Currency (editable)
        Group(
            H6("Currency(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Select(
                Option("Select Currency", value="", disabled=True, selected=True), #"USD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD"
                Option("USD", value="USD"),
                Option("EUR", value= "EUR"),
                Option("JPY", value= "JPY" ),
                Option("GBP" , value="GBP" ),
                Option("AUD", value="AUD" ),
                Option("CHF" , value="CHF" ),
                Option("CAD" , value= "CAD"),
                Option("CNY", value="CNY" ),
                Option("SEK" , value="SEK" ),
                Option("NZD" , value="NZD" ),
                id="currency",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Cost in currency (editable)
        Group(
            H6("Cost in Currency(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="cost_currency", type="float", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        
        # Total cost (editable and auto-calculated)
        Group(
            H6("Book Availability", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Select(
                Option("Select Availability", value="", disabled=True, selected=True),
                Option("Available", value="Available"),
                Option("Not Available", value="Not Available"),
                id="availability_stage5",
                style="padding: 5px; min-width: 120px; border:1.3px solid #D369A3;"
            ),
            style="display: flex; align-items: center; gap: 10px;"
        ),

         Group(
            H6("Supplier Information(*)", style="margin-right: 10px; min-width: 60px; text-align: left;color: #D369A3; "),
            Input(id="supplier_info", style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Remarks while enquiry", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage5" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        Group(
            H6("Remarks while Ordering", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage6" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),

        # Actions: Save, Delete, Back
       # Button("Save", role="button", style="margin-bottom: 15px;"),

        action="/update-bookstage6", id="edit", method='post'
    )
    return res

def stage7(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage7()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]
    all_stages = fetch.allstage()
    if search1:
        search_lower = search.lower()
        all_items = [
            item for item in all_stages
            if any(search_lower in str(value).lower() for value in item)
        ]
    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage7?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage7?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage7?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage7", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage7?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage7", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Book Available", style="font-weight: 1000; text-align: center;"),
            Th("Supplier Information", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Enquiry", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Ordering", style="font-weight: 1000; text-align: center;"),
            Th("Remarks Afetr Receiving", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;"),
                Td(item[15], style="font-size: smaller; padding: 4px;"),
                Td(item[16], style="font-size: smaller; padding: 4px;"),
                Td(item[17], style="font-size: smaller; padding: 4px;"),
                Td(item[18], style="font-size: smaller; padding: 4px;"),
                Td(item[19], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage7/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage8_from_stage7/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage6_from_stage7/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books  Ordered"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under Enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download books here", href="/downloadstage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Received', card)

async def edit_in_stage7(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage7', role="button", style="margin:15px"),

        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        

        Group(
            H6("Remarks After Received", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage7" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        action="/update-bookstage7", id="edit", method='post'

    )
    return res

def stage8(page: int = 1, sort_by: str = "date_stage_update", order: str = "asc", search: str = "", date_range: str = "all"):
    all_items = fetch.stage8()
    all_items = functions.filter_by_date3(all_items, date_range)
    # Apply search filter
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    all_stages = fetch.allstage()
    if search1:
        search_lower = search.lower()
        all_items = [
            item for item in all_stages
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Sorting logic
    if sort_by in ["date_stage_update"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 14}[sort_by]
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
                A("«", href=f"/stage8?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                  style="margin-right: 10px;font-size: x-large;" +
                        ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/stage8?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large ; " +
                          ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/stage8?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}",
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
        action="/stage8", method="get"
    )
    global_search_box = Form(
        Group(
            Input(type="text", name="search1", value=search1, placeholder="Search...", style="margin-right: 10px; padding: 5px;"),
            Input(type="hidden", name="date_range", value=date_range), 
            Button("Search", type="submit", style="font-weight: 600;"),
            style="display: flex; align-items: center;"
        ),
        action="/search", method="get"
    )
    def get_sort_icon(column):
        if sort_by == column:
            return "▲" if order == "asc" else "▼"
        return "⇅"

    def create_sort_link(column):
        new_order = "asc" if sort_by == column and order == "desc" else "desc"
        return A(
            get_sort_icon(column),
            href=f"/stage8?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}",
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
        action="/stage8", method="get"
    )
    table = Table(
        Tr(
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th(Div("Date_Stage_update", create_sort_link("date_stage_update"),
                   style="display: inline-flex; align-items: center; font-weight: 1000;")),
            Th("Book Available", style="font-weight: 1000; text-align: center;"),
            Th("Supplier Information", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Enquiry", style="font-weight: 1000; text-align: center;"),
            Th("Remarks while Ordering", style="font-weight: 1000; text-align: center;"),
            Th("Remarks Afetr Receiving", style="font-weight: 1000; text-align: center;"),
            Th("Remarks Afetr Processed", style="font-weight: 1000; text-align: center;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;"),
                Td(item[15], style="font-size: smaller; padding: 4px;"),
                Td(item[16], style="font-size: smaller; padding: 4px;"),
                Td(item[17], style="font-size: smaller; padding: 4px;"),
                Td(item[18], style="font-size: smaller; padding: 4px;"),
                Td(item[19], style="font-size: smaller; padding: 4px;"),
                Td(item[20], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage8/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage7_from_stage8/{item[1]}", style="display:block;font-size: smaller;")
                )
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    card = Card(
        H3("Books  Ordered"),
        # H6("This displays the details for Stage 3, including editable fields like cost, currency, and remarks."),
        search_box,
        date_range_options,
        table,
        pagination_controls,
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Books approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under Enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download All", href="/downloadentire", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download books here", href="/downloadstage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            global_search_box,
            style="display: flex; gap: 10px;"  # Flexbox for layout
        )
    )
    return Titled('Books Processed' , card)

async def edit_in_stage8(id: int):
    res = Form(
        Button("Save", role="button", style="margin-bottom: 15px;"),
        A('Back', href='/stage8', role="button", style="margin:15px"),

        Group(
            H6("ISBN", style="margin-right: 10px; min-width: 60px; text-align: left; color: #53B6AC"),
            Input(id="isbn", readonly=True, style ="border:1.3px solid #53B6AC;"),  # Fetch ISBN from the stored data
            style="display: flex; align-items: center; gap: 10px;"
        ),
        
        

        Group(
            H6("Remarks After Processed", style="margin-right: 10px; min-width: 60px; color: #D369A3; text-align: left;"),
            Input(id="remarks_stage8" , style ="border:1.3px solid #D369A3;"),
            style="display: flex; align-items: center; gap: 10px;"
        ),
        action="/update-bookstage8", id="edit", method='post'

    )
    return res

def clubbed(c_id):
    items = fetch.clubbed(c_id)
    table = Table(
        Tr(
            Th("Select", style="font-weight: 1000; text-align: center;"),
            Th("ID", style="font-weight: 1000; text-align: center;"),
            Th("ISBN", style=" align-items: center; font-weight: 1000;"),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Sub Title", style="font-weight: 1000; text-align: center;"),
            Th("Author", style="font-weight: 1000; text-align: center;"),
            Th("Publisher", style="font-weight: 1000; text-align: center;"),
            Th("Edition/Year", style="font-weight: 1000; text-align: center;"),
            Th("Number of Copies", style="font-weight: 1000; text-align: center;"),
            Th("Currency", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th("Purpose of recommendation", style="font-weight: 1000; text-align: center;"),
            Th("Cost in Currency", style="font-weight: 1000; text-align: center;"),
            Th("Approval Status", style="font-weight: 1000; text-align: center;"),
            Th("Approval Remarks", style="font-weight: 1000; text-align: center;"),
            Th("Date_Stage_update",style="display: inline-flex; align-items: center; font-weight: 1000;"),
            Th("Action", style="font-weight: 1000; text-align: center;"),
        ),
        *[
            Tr(
                Td(
                Input(type="checkbox", name="row_checkbox", value=item[0], style="margin: auto;"),  # Checkbox in each row
                style="text-align: center; padding: 4px;"
            ),

                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(item[5], style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px;"),
                Td(item[7], style="font-size: smaller; padding: 4px;"),
                Td(item[8], style="font-size: smaller; padding: 4px;"),
                Td(item[9], style="font-size: smaller; padding: 4px;"),
                Td(item[10], style="font-size: smaller; padding: 4px;"),
                Td(item[11], style="font-size: smaller; padding: 4px;"),
                Td(item[12], style="font-size: smaller; padding: 4px;"),
                Td(item[13], style="font-size: smaller; padding: 4px;"),
                Td(item[14], style="font-size: smaller; padding: 4px;maxwidth: 500px"),
                Td(
                    A("Edit", href=f"/edit-book_stage3/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px; width:130px"),
                    A("Move to Next Stage ", href=f"/move_to_stage4_from_stage3/{item[1]}", style="display:block;font-size: smaller;margin-bottom:3px"),
                    A("Move to Previous Stage ", href=f"/move_to_stage2_from_stage3/{item[1]}", style="display:block;font-size: smaller;"),
                    A("Remove from club", href=f"/remove-club/{item[0]}", style="display:block;font-size: smaller;margin-bottom:3px")
            )
        )
            for item in items
        ],
        id = "book-table",
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )
    card = Card(
            H3("Clubbed Books"),
            table
            )

    return (card)

def globalsearch(page: int = 1, sort_by: str = "date", order: str = "desc", search: str = search1, date_range: str = "all", items_per_page: int = 10):
    # Fetch items and apply filters
    all_items = fetch.allstage()
    all_items = functions.filter_by_date_search(all_items, date_range)

    # Apply sorting only for 'date' and 'email' columns
    if sort_by in ["date_stage_update", "email"]:
        reverse = order == "desc"
        column_index = {"date_stage_update": 6, "email": 3}[sort_by]
        all_items.sort(key=lambda x: x[column_index] if x[column_index] is not None else "", reverse=reverse)


    # Implement the search functionality
    if search:
        search_lower = search.lower()
        all_items = [
            item for item in all_items
            if any(search_lower in str(value).lower() for value in item)
        ]

    # Total items and pagination
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

    # Pagination controls
    pagination_controls = Div(
        *(
            [
                A("«", href=f"/search?page={page - 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
                  style="margin-right: 10px;font-size: x-large;" +
                  ("visibility: hidden;" if page == 1 else "visibility: visible;")),
            ]
            + [
                A(
                    str(i),
                    href=f"/search?page={i}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
                    style="margin-right: 10px; text-decoration: none; font-size: x-large; " +
                    ("font-weight: bold;" if i == page else "font-weight: normal;")
                )
                for i in range(start_page, end_page + 1)
            ]
            + [
                A("»", href=f"/search?page={page + 1}&sort_by={sort_by}&order={order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
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
            href=f"/search?page={page}&sort_by={column}&order={new_order}&search={search}&date_range={date_range}&items_per_page={items_per_page}",
            style="text-decoration: none; font-size: small; margin-left: 5px;"
        )

    
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
    table = Table(
        Tr(
            
            Th("ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Modified_ISBN", style="font-weight: 1000; text-align: center;"),
            Th("Recommender", style="font-weight: 1000; text-align: center;"),
            Th(Div("Email", style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
            Th("Title", style="font-weight: 1000; text-align: center;"),
            Th("Current stage", style="font-weight: 1000; text-align: center;"),
            Th(Div("Recent action Date",  style="""display: inline-flex; align-items: center; font-weight: 1000; text-align: center; justify-content: center;width: 100%; height: 100%;""")),
        ),
        *[
            Tr(
                Td(item[0], style="font-size: smaller; padding: 4px;"),
                Td(item[1], style="font-size: smaller; padding: 4px;"),
                Td(item[2], style="font-size: smaller; padding: 4px;"),
                Td(item[3], style="font-size: smaller; padding: 4px;"),
                Td(item[4], style="font-size: smaller; padding: 4px;"),
                Td(stage_mapping.get(item[5], "Unknown"), style="font-size: smaller; padding: 4px;"),
                Td(item[6], style="font-size: smaller; padding: 4px; maxwidth: 500px")
            )
            for item in current_page_items
        ],
        style="border-collapse: collapse; width: 100%;",
        **{"border": "1"}
    )

    

    card = Card(
        H3("Search"),
        table,    
        header=Div(
            A("Initiated", href="/", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processing", href="/stage2", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approval Pending", href="/stage3", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Approved", href="/stage4", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Under enquiry", href="/stage5", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Ordered", href="/stage6", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Received", href="/stage7", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Processed", href="/stage8", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Duplicates", href="/duplicate", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Approved", href="/notapproved", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Not Available", href="/stage11", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            A("Download details here", href="/downloadsearch", role="button", style="margin-left: 10px; white-space: nowrap ; height:50px; font-weight: 700;"),
            style="display: flex; align-items: center; justify-content: flex-start; padding: 20px; height: 50px; font-weight: 700;"
        ),
    )
    return Titled('Search Details', card)
