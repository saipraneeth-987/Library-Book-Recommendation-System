## Summary ##
The purpose of this program is to create an application to create, read, update
and delete (CRUD) data that is given as input in a CSV file.

## Installation ##
This project uses [fasthtml](https://fastht.ml/). Run the following to install the required packages.

``` bash
pip install python-fasthtml
pip install fastapi
```

## Features
- Maintain data.
- Backup and restore data as CSV
- Periodic backups

## Running ## 
To run, do

``` bash
python3 crud.py
```
Data is stored in sqlite format in `data/data.db`.
