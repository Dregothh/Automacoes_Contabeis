import os
import requests
import sqlite3
import time
from bs4 import BeautifulSoup

# Connect to SQLite database
prod_db = sqlite3.connect('oficina.db')
prod_dbc = prod_db.cursor()

# Define table name
table = 'produtos'

# Check if table exists
prod_dbc.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
table_exists = prod_dbc.fetchone() is not None

if not table_exists:
    # Create the table if it doesn't exist
    prod_dbc.execute(f"""
        CREATE TABLE {table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            produto TEXT,
            ncm TEXT
        )
    """)

    # Define the base folder containing the XML files
    base_folder = 'C:/Users/nelso/Desktop/CANAL DA PECA XMLs'

    # Collect all file paths from the base folder
    files = [os.path.join(base_folder, file) for file in os.listdir(base_folder)]

    # Extract URLs from XML files and store in the database
    for file in files:
        with open(file, 'r', encoding='utf-8') as file:
            xmlfile = file.read()

        soup = BeautifulSoup(xmlfile, 'xml')
        urls = [url.text for url in soup.find_all('loc')]

        for url in urls:
            # Insert URLs into the database if they don't already exist
            prod_dbc.execute(f"""
                INSERT OR IGNORE INTO {table} (url) VALUES (?)
            """, (url,))
        prod_db.commit()

# Fetch all rows where 'produto' or 'ncm' is NULL
prod_dbc.execute(f"""
    SELECT id, url FROM {table} WHERE produto IS NULL OR ncm IS NULL
""")
rows_to_scrape = prod_dbc.fetchall()

# Initialize timer and counter
start_time = time.time()
scraped_count = 0
pending_operations = 0
batch_size = 50

# Scrape the data for rows with NULL values
for idx, row in enumerate(rows_to_scrape):
    row_id, url = row
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        product = soup.find('h1', class_='product__name')
        rows = soup.find_all('tr', class_='row no-gutters')

        ncm_num = None
        ncm_present = False
        for tr in rows:
            th = tr.find('th')
            if th and th.text.strip().casefold() == 'ncm':
                td = tr.find('td', class_='col-xs-8 col-sm-8 col-md-8 col-lg-8')
                if td:
                    ncm_num = td.text.strip()
                    ncm_present = True

        # Increment scraped count for every processed row
        scraped_count += 1
        pending_operations += 1

        if not ncm_present:
            # Delete the row if NCM is not present
            prod_dbc.execute(f"""
                DELETE FROM {table} WHERE id = ?
            """, (row_id,))
        else:
            if product and ncm_num:
                product = product.text.strip()
                ncm_num = ncm_num.replace('.', '')

                # Update the row in the database
                prod_dbc.execute(f"""
                    UPDATE {table} SET produto = ?, ncm = ? WHERE id = ?
                """, (product, ncm_num, row_id))

        # Commit every batch_size operations
        if pending_operations >= batch_size:
            prod_db.commit()
            print(f'\n\nCOMMITTING...\n\n')
            pending_operations = 0

        # Calculate average scrape rate
        elapsed_time = time.time() - start_time
        avg_rate = scraped_count / elapsed_time if elapsed_time > 0 else 0

        print(f"Current row: {row_id}\nScraping Rate: {avg_rate:.2f} URLs/second\n")

# Final commit for remaining operations
if pending_operations > 0:
    print(f'\n\nCOMMITTING AND FINISHING...\n\n')
    prod_db.commit()

prod_db.close()
