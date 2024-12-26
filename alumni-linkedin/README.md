## Summary ##

**Project scrapped as Linkedin does not give any access to their data without paying $$$**
The purpose of this program is to fetch the following
information of alumni who have graduated from IIT Palakkad. The expected
details are:

- Roll number (from csv)
- Linkedin URL (from csv)
- Year of passing out (from csv)
- Name
- Sector
- Name of current organization
- Designation
- Current Location
- State
- Country
- Continent
- Total years of experience
- Previous company and experience in years
- Highest education


## Requirements ##
A web interface to fetch the data when required and display. Also an option to download all the data as a CSV.

The details also needs to be displayed as a table with functionality to filter
based on year of graduation, roll number and name.

## Installation ##
This project uses [fasthtml](https://fastht.ml/). Run the following to install the required packages.

``` bash
pip install python-fasthtml
pip install fastapi
```

## Features ##
- Uses Linkedin API to access data
- Allow data to be given as a CSV (roll number, linkedin url, year of passing out).
- Displays appropriate error messages for information that was not found.

## Running ## 
To run, do

``` bash
python3 alumni.py
```
Data is stored in sqlite format in `data/data.db`.
