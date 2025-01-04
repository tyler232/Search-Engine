import mysql.connector
import re
from collections import Counter

class Database:
    def __init__(self, db_config):
        self.db_config = db_config
        self.db_connection = None
        self.db_cursor = None
        self.connect_to_db()

    def connect_to_db(self):
        """Establish connection to the MySQL database."""
        try:
            self.db_connection = mysql.connector.connect(**self.db_config)
            self.db_cursor = self.db_connection.cursor()
            print("Database connected successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection = None
            self.db_cursor = None

    def insert_webpage(self, url, title, content):
        """Insert crawled data into the 'webpages' table."""
        if self.db_cursor and self.db_connection:
            try:
                insert_query = """
                    INSERT INTO webpages (url, title, text)
                    VALUES (%s, %s, %s)
                """
                self.db_cursor.execute(insert_query, (url, title, content))
                self.db_connection.commit()
                print(f"Webpage data inserted for: {url}")
                return self.db_cursor.lastrowid  # Return the ID of the newly inserted row
            except mysql.connector.Error as err:
                print(f"Error inserting webpage data: {err}")
                return None

    def insert_word_frequencies(self, url_id, frequency_data):
        """Insert word frequencies into the 'word_frequencies' table using bulk insert."""
        if self.db_cursor and self.db_connection:
            try:
                insert_query = """
                    INSERT INTO word_frequencies (url_id, word, frequency)
                    VALUES (%s, %s, %s)
                """
                # Prepare data for bulk insert
                values_to_insert = [(url_id, word, int(freq)) for word, freq in frequency_data.items()]
                
                # Execute bulk insert
                self.db_cursor.executemany(insert_query, values_to_insert)
                self.db_connection.commit()

                print(f"Word frequencies inserted for URL ID: {url_id}")
            except mysql.connector.Error as err:
                print(f"Error inserting word frequencies: {err}")

    def get_url_id(self, url):
        """Retrieve the URL ID from the 'webpages' table."""
        if self.db_cursor and self.db_connection:
            try:
                select_query = """
                    SELECT id FROM webpages WHERE url = %s
                """
                self.db_cursor.execute(select_query, (url,))
                result = self.db_cursor.fetchone()
                return result[0] if result else None
            except mysql.connector.Error as err:
                print(f"Error retrieving URL ID: {err}")
                return None
    
    def insert_backlink(self, from_url_id, to_url_id):
        """Insert backlink data into the 'backlinks' table."""
        if from_url_id != to_url_id and self.db_cursor and self.db_connection:
            try:
                insert_query = """
                    INSERT INTO backlinks (from_url_id, to_url_id)
                    VALUES (%s, %s)
                """
                self.db_cursor.execute(insert_query, (from_url_id, to_url_id))
                self.db_connection.commit()
                print(f"Backlink inserted from {from_url_id} to {to_url_id}")
            except mysql.connector.Error as err:
                print(f"Error inserting backlink: {err}")

    def close_connection(self):
        """Close the database connection."""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_connection:
            self.db_connection.close()
            print("Database connection closed.")
