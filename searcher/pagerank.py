import mysql.connector
import os
from dotenv import load_dotenv

def calculate_pagerank(db_connection, damping_factor=0.85, iterations=10):
    cursor = db_connection.cursor(dictionary=True)
    
    # get all the webpages
    cursor.execute("SELECT id FROM webpages")
    pages = cursor.fetchall()
    page_ids = [page['id'] for page in pages]
    print(f"Page IDs: {page_ids}")
    
    # Initialize pagerank values to 1
    for page_id in page_ids:
        cursor.execute("UPDATE webpages SET pagerank = 1.0 WHERE id = %s", (page_id,))
    db_connection.commit()
    
    for _ in range(iterations):
        for page_id in page_ids:
            cursor.execute("""
                SELECT from_url_id, COUNT(*) as outlinks
                FROM backlinks WHERE to_url_id = %s
                GROUP BY from_url_id
            """, (page_id,))
            backlinks = cursor.fetchall()
            
            new_pagerank = 0.0
            for backlink in backlinks:
                from_url_id = backlink['from_url_id']
                outlinks = backlink['outlinks']
                
                cursor.execute("SELECT pagerank FROM webpages WHERE id = %s", (from_url_id,))
                from_pagerank = cursor.fetchone()['pagerank']
                
                new_pagerank += from_pagerank / outlinks

            cursor.execute("""
                UPDATE webpages
                SET pagerank = %s
                WHERE id = %s
            """, ((1 - damping_factor) + damping_factor * new_pagerank, page_id))

        db_connection.commit()

    cursor.close()
    print("PageRank calculation completed.")  # Debugging line

if __name__ == "__main__":
    load_dotenv()
    db = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
        "database": os.getenv("DB_NAME")
    }

    connection = mysql.connector.connect(**db)
    calculate_pagerank(connection)
    connection.close()
