## Summary ##
This project is for the institute library. The purpose of this project is to
automate part of the book recommendation workflow which is currently being done
through google sheets.

The context for this project is the following: 
- we have a [book recommendation system](https://docs.google.com/forms/d/e/1FAIpQLSfgUek_iRK71V2WYsErVSfoAb-YQu5_HjTvTyRntAKNjClh9Q/viewform?usp=sf_link) in the institute.
- there are several stages of the book acquisition which the librarian has to
manually maintain in huge spreadsheets.
- this is creating difficulty as the volume of all new purchase data that the
library is getting high. This is only going to grow as the institute grows.

To help the librarian, we need to build a chhootu webpage that can help track all the requests and their stages.

## Stages of a book acquisition ##

* Stage 1: Book request raised
    - The google form in the link above is used to collects the details of the new book.
    - All the data (ISBN, number of copies, recommender) is collected and stored in a google sheet.
    - Desirable information to be maintained in this stage are
        * ISBN (non editable, number)
        * Recommender (non editable, text)
        * Number of copies (non editable, text)
        * Purpose of recommendation (non editable, text)
        * Remarks (non editable, text)
        * Name of recommender (non editable, text)
        * Date on which request is placed (non editable, text).

* Stage 2: Processing and Invoice generation
    - The librarian takes the newly recommended books and finds the correct
    book title (using ISBN), authors and publisher details.  
    - From various website (like Amazon/Cambridge Uni Press/Elsevier) the cost
    of the book (and the currency) is found out and added. Also cost in INR is
    calculated.
    - Once all of this is done, an invoice (a statement that lists all the book
    titles, ISBN, authors, publisher, number of copies and cost)
    - Desirable information to be maintained and displayed in this stage are
        * ISBN (non editable, from stage 1)
        * Modified ISBN (by default, it is same as ISBN, editable)
        * Name of recommender (non editable, from stage 1)
        * Number of copies (editable, number)
        * Name of book (editable, text)
        * Remarks (editable, specifc for stage 2 (don't copy from stage 1))
        * Publisher (editable, text)
        * Author names (editable, text)
        * Currency  (editable, text)
        * Cost in currency (editable, number)
        * Cost in INR (editable, number)
        * Total cost (editable, number, automatically calculated from the given data)
        * Date on which request is placed (non editable, from stage 1)

* Stage 3: Submitted for Approval from Dean Academics
    - The invoice prepared in Stage 1 is emailed to Dean Academics who will approve or not approve.
    - If approved, the book moves to the next stage. If not, the process ends here.
    - Desirable information to be maintained and displayed in this stage are
        * ISBN (non editable, from stage 2)
        * Name of book (non editable, from stage 2)
        * Number of copies (non editable, from stage 2)
        * Currency  (editable, text)
        * Cost in currency (editable, number)
        * Cost in INR (editable, number)
        * Date on which stage 2 is completed (non editable, autocalculated based on when stage 1 is completed)
        * Status of approval from Dean academics (editable, Boolean: approved/not approved)
        * Remarks (editable, specifc for stage 3 (don't copy from stage 2))
        
* Stage 4: Placing purchase order
    - Librarian then obtain quotes from online/offline vendors and places the purchase order

* Stage 5: Book acquisition 
    - The book has arrivied in the library. The books bundle needs to be opened
    and proper cataloging needs to be done.

* Stage 6: Book in circulation
    - Once stage 4 is over, the book is ready for circulation.

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
{1,2,3,4,5}) should be provided.


