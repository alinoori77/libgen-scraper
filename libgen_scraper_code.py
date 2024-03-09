import requests  # Importing requests library for making HTTP requests
from bs4 import BeautifulSoup  # Importing BeautifulSoup for parsing HTML
import pandas as pd  # Importing pandas for data manipulation and analysis
import os  # Importing os module for interacting with the operating system
from datetime import datetime  # Importing datetime for working with dates and times
import argparse  # Importing argparse for parsing command-line arguments
from database_manager import DatabaseManager
import sample_settings
import peewee



database_manager = DatabaseManager(
    database_name=sample_settings.DATABASE['name'],
    user=sample_settings.DATABASE['user'],
    password=sample_settings.DATABASE['password'],
    host=sample_settings.DATABASE['host'],
    port=sample_settings.DATABASE['port'],
)

class Author(peewee.Model):
    title = peewee.CharField(max_length=2048, null=False, verbose_name='Title')
    class Meta:
        database = database_manager.db


class Book(peewee.Model):
    Name = peewee.CharField(max_length=2048, null=False, verbose_name='Title')
    Author = peewee.ForeignKeyField(model=Author, null=False, verbose_name='Author')
    Publisher = peewee.CharField(max_length=2048, null=False, verbose_name='Publisher')
    language = peewee.CharField(max_length=2048, null=False, verbose_name='language')
    p_a_g_e = peewee.CharField(max_length=2048, null=False, verbose_name='Pages')


    class Meta:
        database = database_manager.db

def scrape_books(book_name):

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
    database_manager.create_tables(models=[Author, Book])

    for book in books:
        author, _ = Author.get_or_create(title=book['author'])
        Book.get_or_create(Name =str(book["title"]),Author=author ,Publisher=str(book['Publisher']),p_a_g_e=str(book['Pages']),language=str(book['language']))


def export_data(format, book_name):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Getting current date and time
    folder_name = f"{current_time}_{book_name}"  # Creating folder name based on current time and book name
    os.makedirs(folder_name, exist_ok=True)  # Creating folder to store exported files




    
    # Exporting data based on the specified format
    if format == 'xls':

        # Fetch data from the database where post title
        query = Book.select().where(Book.Name == book_name)

        # Convert the query result to a pandas DataFrame
        df = pd.DataFrame(list(query.dicts()))

        # Export DataFrame to an Excel file
        df.to_excel(os.path.join(folder_name, f"{book_name}.xlsx"), index=False)

        # Close the database connection
        database_manager.db.close()

    elif format == 'json':

        # Fetch data from the database where post title 
        query = Book.select().where(Book.Name == book_name)

        # Convert the query result to a pandas DataFrame
        df = pd.DataFrame(list(query.dicts()))

        # Export DataFrame to an Excel file
        df.to_json(os.path.join(folder_name, f"{book_name}.json"), index=False)

        # Close the database connection
        database_manager.db.close()
        
    elif format == 'csv':

        # Fetch data from the database where post 
        query = Book.select().where(Book.Name == book_name)
        # Convert the query result to a pandas DataFrame
        df = pd.DataFrame(list(query.dicts()))

        # Export DataFrame to an Excel file
        df.to_csv(os.path.join(folder_name, f"{book_name}.csv"), index=False)

        # Close the database connection
        database_manager.db.close()



def main():
    """
    Main function to initiate the book data scraping and exporting process.
    """
    parser = argparse.ArgumentParser(description="Scrape book data from Libgen and export it.")
    parser.add_argument("book_name", type=str, help="Name of the book")
    parser.add_argument("export_format", type=str, choices=['xls', 'json', 'csv'],help="Export format (xls/json/csv)")
    args = parser.parse_args()

    book_name = args.book_name  # Retrieving book name from command-line arguments
    books = scrape_books(book_name)  # Scraping book data from Libgen
    save_to_database(books)  # Saving scraped data into SQLite database







    # export_format = args.export_format  # Retrieving export format from command-line arguments
    # export_data(export_format, book_name)  # Exporting scraped data in the specified format


if __name__ == "__main__":
    main()  # Calling the main function when the script is executed
