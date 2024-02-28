import requests  # Importing requests library for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for parsing HTML
import sqlite3  # Importing sqlite3 for working with SQLite database
import json  # Importing json module for working with JSON data
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os module for interacting with the operating system
from datetime import datetime  # Importing datetime for working with dates and times
import argparse  # Importing argparse for parsing command-line arguments
import zipfile  # Importing zipfile for working with zip files


def scrape_books(book_name):
    """
    Function to scrape book data from Libgen based on the provided book name.

    :param book_name: Name of the book to search for
    :return: List of dictionaries containing book information
    """
    page_number = 1
    book_results = list()  # Initialize an empty list to store book information

    while True:
        # Constructing the URL for searching books on Libgen
        url = f"https://libgen.is/search.php?&req={book_name}&phrase=1&view=simple&column=def&sort=def&sortmode=ASC&page={page_number}"
        response = requests.get(url)  # Sending HTTP GET request
        soup = BeautifulSoup(response.text, 'html.parser')  # Parsing the HTML response

        check_valid_page = soup.find_all('tr', valign='top')
        # Checking if the page has valid results or not
        if len(check_valid_page) == 1:
            break  # Break the loop if no valid results are found
        else:
            # Iterating through each row in the search results table
            for row in soup.find_all('tr', valign='top'):
                cells = row.find_all('td')  # Extracting individual cells in the row
                if cells[1].text.strip() == "Author(s)":
                    continue  # Skipping the header row
                # Extracting book information from each cell and storing it in a dictionary
                book_info = {
                    'ID': cells[0].text.strip(),
                    'author': cells[1].text.strip(),
                    'title': cells[2].text.strip(),
                    'Publisher': cells[3].text.strip(),
                    'Year': cells[4].text.strip(),
                    'Pages': cells[5].text.strip(),
                    'language': cells[6].text.strip(),
                    'link': [i for i in cells[2].find_all('a') if i['href'].startswith('book/')][0].get("href")
                }
                book_results.append(book_info)  # Adding book information to the list
        page_number = page_number + 1  # Incrementing page number for next page

    return book_results  # Returning the list of book information


def save_to_database(books):
    """
    Function to save scraped book data into SQLite database.

    :param books: List of dictionaries containing book information
    :return: None
    """
    conn = sqlite3.connect('book_data.db')  # Connecting to SQLite database
    c = conn.cursor()  # Creating a cursor object for executing SQL queries

    # Creating 'authors' table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY,
                    name TEXT)''')

    # Creating 'books' table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    author_id INTEGER,
                    Publisher TEXT,
                    Year TEXT ,
                    Pages TEXT ,
                    language TEXT ,
                    FOREIGN KEY (author_id) REFERENCES authors(id))''')

    # Creating 'search_results' table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY,
                    result TEXT)''')

    # Iterating through each book in the list and saving its information into the database
    for book in books:
        author_id = c.execute("SELECT id FROM authors WHERE name=?", (book['author'],)).fetchone()
        if not author_id:
            c.execute("INSERT INTO authors (name) VALUES (?)", (book['author'],))
            author_id = c.lastrowid
        else:
            author_id = author_id[0]

        book_id = c.execute("SELECT id FROM books WHERE name=?", (book['title'],)).fetchone()
        if not book_id:
            c.execute("INSERT INTO books (name, author_id , Publisher ,Year ,Pages ,language) VALUES (?, ? ,?,?,?,?)",
                      (book['title'], author_id, book['Publisher'], book['Year'], book['Pages'], book['language']))
            book_id = c.lastrowid
        else:
            book_id = book_id[0]

        conn.commit()  # Committing the transaction to save changes into the database

    conn.close()  # Closing the database connection


def export_data(format, book_name):
    """
    Function to export scraped book data in the specified format.

    :param format: Export format (xls/json/csv)
    :param book_name: Name of the book
    :return: None
    """
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Getting current date and time
    folder_name = f"{current_time}_{book_name}"  # Creating folder name based on current time and book name
    os.makedirs(folder_name, exist_ok=True)  # Creating folder to store exported files

    conn = sqlite3.connect('book_data.db')  # Connecting to SQLite database
    df = pd.read_sql_query("SELECT * FROM books", conn)  # Reading data from 'books' table into a DataFrame
    conn.close()  # Closing the database connection

    # Exporting data based on the specified format
    if format == 'xls':
        df.to_excel(os.path.join(folder_name, f"{book_name}.xlsx"), index=False)
    elif format == 'json':
        df.to_json(os.path.join(folder_name, f"{book_name}.json"), orient='records')
    elif format == 'csv':
        df.to_csv(os.path.join(folder_name, f"{book_name}.csv"), index=False)


def main():
    """
    Main function to initiate the book data scraping and exporting process.
    """
    parser = argparse.ArgumentParser(description="Scrape book data from Libgen and export it.")
    parser.add_argument("book_name", type=str, help="Name of the book")
    parser.add_argument("export_format", type=str, choices=['xls', 'json', 'csv'],
                        help="Export format (xls/json/csv)")
    args = parser.parse_args()

    book_name = args.book_name  # Retrieving book name from command-line arguments
    books = scrape_books(book_name)  # Scraping book data from Libgen
    save_to_database(books)  # Saving scraped data into SQLite database

    export_format = args.export_format  # Retrieving export format from command-line arguments
    export_data(export_format, book_name)  # Exporting scraped data in the specified format


if __name__ == "__main__":
    main()  # Calling the main function when the script is executed
