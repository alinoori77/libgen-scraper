import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import pandas as pd
import os
from datetime import datetime
import argparse



def scrape_books(book_name):
    page_number = 1
    book_results = list()

    while True:
        url = f"https://libgen.is/search.php?&req={book_name}&phrase=1&view=simple&column=def&sort=def&sortmode=ASC&page={page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        check_valid_page = soup.find_all('tr', valign='top')
        if len(check_valid_page) == 1:
            break
        else:
            for row in soup.find_all('tr', valign='top'):
                cells = row.find_all('td')
                if cells[1].text.strip() == "Author(s)":
                    continue
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
                book_results.append(book_info)
        page_number = page_number+1

    return book_results

def save_to_database(books):
    conn = sqlite3.connect('book_data.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY,
                    name TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    author_id INTEGER,
                    Publisher TEXT,
                    Year TEXT ,
                    Pages TEXT ,
                    language TEXT ,
                    FOREIGN KEY (author_id) REFERENCES authors(id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY,
                    result TEXT)''')
    

    for book in books:  
        author_id = c.execute("SELECT id FROM authors WHERE name=?", (book['author'],)).fetchone()
        if not author_id:
            c.execute("INSERT INTO authors (name) VALUES (?)", (book['author'],))
            author_id = c.lastrowid
        else:
            author_id = author_id[0]

        book_id = c.execute("SELECT id FROM books WHERE name=?", (book['title'],)).fetchone()
        if not book_id:
            c.execute("INSERT INTO books (name, author_id , Publisher ,Year ,Pages ,language) VALUES (?, ? ,?,?,?,?)", (book['title'], author_id , book['Publisher'] , book['Year'], book['Pages'], book['language']))
            book_id = c.lastrowid
        else:
            book_id = book_id[0]

        conn.commit()

    conn.close()




def export_data(format, book_name):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{current_time}_{book_name}"
    os.makedirs(folder_name, exist_ok=True)

    conn = sqlite3.connect('book_data.db')
    df = pd.read_sql_query("SELECT * FROM books", conn)
    if format == 'xls':
        df.to_excel(os.path.join(folder_name, f"{book_name}.xlsx"), index=False)
    elif format == 'json':
        df.to_json(os.path.join(folder_name, f"{book_name}.json"), orient='records')
    elif format == 'csv':
        df.to_csv(os.path.join(folder_name, f"{book_name}.csv"), index=False)
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Scrape book data from Libgen and export it.")
    parser.add_argument("book_name", type=str, help="Name of the book")
    parser.add_argument("export_format", type=str, choices=['xls', 'json', 'csv'], help="Export format (xls/json/csv)")
    args = parser.parse_args()

    book_name = args.book_name
    books = scrape_books(book_name)
    save_to_database(books)

    export_format = args.export_format
    export_data(export_format, book_name)

if __name__ == "__main__":
    main()