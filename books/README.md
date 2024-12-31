## Summary ##
This project is for the institute library. The purpose of this project is to
automate part of the book recommendation workflow which is currently being done
through google sheets.

The context for this project is the following: 

- we have a [book recommendation system](https://docs.google.com/forms/d/e/1FAIpQLSfgUek_iRK71V2WYsErVSfoAb-YQu5_HjTvTyRntAKNjClh9Q/viewform?usp=sf_link) in the institute.

- there are several stages of the book acquisition which the librarian has to manually maintain in huge spreadsheets.

- this is creating difficulty as the volume of all new purchase data that the library is getting high. This is only going to grow as the institute grows.

To help the librarian, we need to build a chhootu webpage that can help track all the requests and their stages.

## Stages of a book acquisition ##

* Stage 1: Book request raised (Stage = Initiated)
    - The google form in the link above is used to collects the details of the new book.
    - All the data (ISBN, number of copies, recommender) is collected and stored in a google sheet.
    - Desirable information to be maintained in this stage are
        * ISBN (non editable, number, mandatory)
        * Number of copies (non editable, text, mandatory)
        * Purpose of recommendation (non editable, text, mandatory)
        * Remarks (non editable, text, optional)
        * ~~Name of recommender~~ Recommender (non editable, text, mandatory)
        * Date on which request is placed (non editable, date).
	* Stage (non editable, must be fixed as "Initiated")
    - Desirable Features
	* [X] At the beginning of the page for stage 1, explain what the stage does (as a small description para).
    	* [X] Display this information as table with appropriate headers. 
	* [X] Make the data sortable by the date column. 
	* [X] Ability to select entries based on date (1 month, 3 month and so on)
	* [X] After the description of the page, add a button which upon clicking moves the entries whose checkbox are selected over to stage 2.
	* [ ] New field on stage. Stages can be one of Initiated, Processing, Duplicate, Approved, Under enquiry, Ordered, Received, Processed, Not available.

* Stage 2: Processing (Stage = Processing)
    - The librarian takes the newly recommended books and finds the correct
    book title (using ISBN), authors and publisher details.  
    - From various website (like Amazon/Cambridge Uni Press/Elsevier) the cost
    of the book (and the currency) is found out and added. Also cost in INR is
    calculated.
    - Once all of this is done, an invoice (a statement that lists all the book
    titles, ISBN, authors, publisher, number of copies and cost)
    - Desirable information to be maintained and displayed in this stage are
        * ISBN (non editable, from stage 1)
        * Modified ISBN (by default, it is same as ISBN, editable, mandatory)
        * Recommender (non editable, from stage 1)
        * Number of copies (editable, number, from stage 1)
        * ~~Name of book~~ Title (editable, text, mandatory)
        * Sub Title (editable, text, optional)
        * Purpose of recommendation (non editable, from stage 1)
        * Remarks (editable, specific for stage 2 (don't copy from stage 1))
        * Publisher (editable, text, mandatory)
        * Edition/Year  (editable, text, mandatory)
        * ~~Author names~~ Author (editable, text, mandatory)
        * Currency  (editable, mandatory, dropdown - standard three letter currency names ISO standard. See [here](https://currencysystem.com/codes/))
        * Cost in currency per book (editable, mandatory, ~~number~~ floating point number)
        * Date on which request is placed (non editable, from stage 1)
	* Book available ? (editable, mandatory, Dropdown Yes/No)
	* Stage (non editable, must be fixed as "Processing")
    - Desirable features
	* [X] Ability to sort based on email and date column
	* [X] Pagination of data displayed. Display max 10 books.
	* [ ] Ability to also list first 20, 50 and 100 books (in addition to pagination)
	* [X] Once the Modified ISBN is entered, use public service API (openlibrary) and fetch the book title name, authors and the publisher information.
	* [ ] Z39.50 based [library data access](https://wiki.koha-community.org/wiki/Configure_Z39.50/SRU_targets) or Google Books [API](https://developers.google.com/books/docs/v1/using). Google books requires an API key.
	* [X] Download of books specific to a given stage.
	* [ ] While filling details, show error message if mandatory fields are not entered during submission.
	* [ ] Color code fields that are editable (as green) and those that are not editable (as red)
	* [ ] Give star in front of fields that are mandatory
	* [ ] New field on stage. Stages can be one of Initiated, Processing, Duplicate, Approval pending, Under enquiry, Ordered, Received, Processed, Not available.
	* [ ] For books that are already available (the "Book available ?" field marked as yes), add an option to move the entry to a new stage called "Duplicate".
	* [ ] For certain entries that were multiply submitted (accidently in the google form) needs to be "Duplicate".
	* [ ] New field on stage. Stages can be one of Initiated, Processing, Duplicate, Approval pending, Under enquiry, Ordered,	Received, Processed, Not available.
	* [ ] New field on Edition/Year. 
	* [ ] Get recommender name from email address via Gmail API. 

* Stage 3: Submitted for Approval from Dean Academics (Stage = Approval pending)
    - The invoice prepared in Stage 2 is emailed to Dean Academics who will approve or not approve. This stage prepares the relevant data.
    - Desirable information to be maintained and displayed in this stage are
        * ISBN (non editable, same as Modified ISBN from stage 2)
        * Title (non editable, from stage 2)
        * Subtitle (non editable, from stage 2)
	* Author (non editable, from stage 2)
	* Publisher (non editable, from stage 2)
	* Edition/Year (non editable, from stage 2)
        * Number of copies (non editable, from stage 2)
        * Currency  (non editable, from stage 2)
        * Recommender (non editable, from stage 1)
        * Purpose of recommendation (non editable, from stage 2)
        * Cost in currency (non editable, from stage 2)
        * Status of approval from Dean academics (editable, dropdown - Pending/Approved/Not approved). Default value: Pending
        * Date on which stage 2 is completed (non editable, autocalculated based on when stage 1 is completed)
        * Remarks (editable, specific for stage 3 (don't copy from stage 2))
    - Desirable features
	* Club requests
	  - [ ] Ability to select a non-empty subset of requests clubbed together and move them together as one entity to the next stage for approval. Possibly do this via a check box.
	  - [ ] The books that are clubbed together must be displayed together.
	  - [ ] For the selected books, a text message needs to be generated in a certain format (Format given in `bulk.docx`)
	* [ ] New field on stage. Stages can be one of Initiated, Processing, Duplicate, Approved, Under enquiry, Ordered, Received, Processed, Not available.
	 
* Stage 4: Approved (Stage = Approved)
    - All the approved books from the previous stage comes here.
    - If approved, the book moves to the next stage. If not, the process ends here
    - Desirable information to be maintained and displayed in this stage are
	* All details from stage 3
        * Status of approval from Dean academics (not editable, dropdown - Approved/Not approved). Default value: Approved
        * Remarks (editable, specific for stage 4 (don't copy from stage 3))
    - Desirable features
	* [ ] New field on stage. Stages can be one of Initiated, Processing, Duplicate, Approved, Under enquiry, Ordered, Received, Processed, Not available, Not approved.
	* [ ] Books that are not approved must be moved to Not approved stage. Move to Not approved stage must be enabled if the status is not approved.
	* [ ] Books that are approved must be allowed to move to the next stage.
	* [ ] Requests need not be shown as clubbed anymore.

* Stage 5: Book acquisition  (Stage = Under enquiry)
    - Librarian has placed the request to get book quotes with sellers for availability.
    - Desirable information to be maintained and displayed in this stage are
	* All details from stage 4. All are not editable.
	* Book is available / not available (editable, dropdown, Yes/No)
	* Supplier information (editable, text, mandatory if book is available)
        * Remarks (editable, specific for stage 5 (don't copy from stage 4))
    - Desirable features	
	* [X] Ability to download all the titles in this stage as a CSV
	* [ ] If the book is available field is yes, move to the next stage. Else move to the "Not available" stage.

* Stage 6: Order placed (Stage = ordered)
    - Order is placed with the supplier.
    - Desirable information to be maintained and displayed in this stage are
	* All details from stage 5. **All details must be editable**
        * Remarks (editable, specific for stage 6 (don't copy from stage 5))
    - Desirable features	
	* [X] Ability to download all the titles with the info "Title, Subtitle, Author, Publisher, ISBN, Edition/Year, Price, No of copies" as a CSV.

* Stage 7: Received (stage = Received)
    - The book has arrived in the library. The books bundle needs to be opened and proper cataloging needs to be done.
    - Desirable information to be maintained and displayed in this stage are
	* All details from stage 6. All are not editable.
        * Remarks (editable, specific for stage 7 (don't copy from stage 6))

* Stage 8: Our for circulation (stage = Processed)
    - The book is now in circulation.
    - Desirable information to be maintained and displayed in this stage are
        * All details from stage 7. All are not editable.
        * Remarks (editable, specific for stage 8 (don't copy from stage 7))

* Stage Not approved (stage = Not approved)
    - Contains all those books that are not approved by Dean acads.
    - Should display all the usual information.
    - [ ] Should allow move back to stage 3.

* Stage Duplicate (stage = Duplicate)
    - Should display all the usual information.
    - Contains books that have been cancelled due to accidental duplicates in google form.
    - [ ] Should allow move back to stage 1.

* Stage Not available (stage = Not available)
    - Should display all the usual information.
    - Contains books that is not available with the book vendors.
    - [ ] Should allow move back to stage 5.


* Global search
    - Link to search functionality must  appear in all pages.
    - [ ] A separate page to find the status of a book based on
	* ISBN and
	* Recommender and
	* Title
    - [ ] If a field is empty, do not use it in search.
    - [ ] The search should display all the info that is matching.
    - [ ] Ability to download data as csv

## Implementation ##
You can assume that the list of new books is given as a CSV file (sample
CSV added to the repo). This will be the input to Stage 1.

Create a separate page for each stage displaying the relevant information (like
a spreadsheet with proper header ISBN, title etc) but without any ability to
edit them. Each page should list a max of 10 books. The remaining books must be
[paginated](https://www.w3schools.com/howto/howto_css_pagination.asp) and
displayed.

After the list of the books are displayed, at the end of each stage (except the
last stage), there is a button which upon clicking will move all those books
selected in that stage (using check boxes) to be moved to the next stage.

In each stage, a short description of the stage should be provided at the
beginning. Also, a facility to download the books in stage i (for i in
{1,2,3,4,5,6,7,8}) should be provided.


