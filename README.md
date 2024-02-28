Introduction

This script is designed to scrape book data from Libgen (Library Genesis), a website offering free access to a vast collection of books, and export the data in various formats such as Excel, JSON, or CSV. The script utilizes web scraping techniques to retrieve book information based on the provided book name.

Prerequisites
Before running the script, ensure you have the following prerequisites installed:

Python 3.x
Necessary Python libraries (install using pip install -r requirements.txt):
requests
BeautifulSoup (bs4)
pandas
SQLite3
Usage
To use the script, follow these steps:

Clone or download the script to your local machine.
Open a terminal or command prompt.
Navigate to the directory where the script is located.
Run the script using the following command:
python script_name.py book_name export_format
Replace script_name.py with the name of the Python script file.
Replace book_name with the name of the book you want to search for.
Replace export_format with the desired export format (xls, json, or csv).

Example
Here's an example of how to use the script:

python scraper.py "Python Programming" json
This command will scrape book data related to "Python Programming" from Libgen and export it in JSON format.

Output
The script will create a folder named with the current timestamp along with the book name (e.g., 2024-02-28_17-30-45_Python Programming). Inside this folder, the exported file will be saved with the provided book name and the specified format (e.g., Python Programming.json).

Notes
The script interacts with Libgen's website, so any changes to the website's structure may affect its functionality.
Use this script responsibly and ensure compliance with Libgen's usage policies and legal regulations regarding web scraping.
Acknowledgments
This script utilizes the following Python libraries: requests, BeautifulSoup, sqlite3, json, pandas, os, datetime, and argparse. Special thanks to the developers of these libraries for their contributions.
If you encounter any issues or have suggestions for improvement, feel free to open an issue or contribute to the repository. Happy scraping!




