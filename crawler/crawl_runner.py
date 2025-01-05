from crawler import WebCrawler
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
NUM_THREADS = int(os.getenv("NUM_THREADS"))
CRAWL_LIMIT = int(os.getenv("CRAWL_LIMIT"))

if __name__ == "__main__":
    db = {
        "host": DB_HOST,
        "user": DB_USER,
        "password": DB_PASS,
        "database": DB_NAME
    }
    
    starting_urls = [
        "https://illinois.edu",
        "https://en.wikipedia.org/wiki/University_of_Illinois_Urbana-Champaign",
        "https://www.usnews.com/best-colleges",
        "https://www.coursera.org"
    ]

    # setup Indexer before crawling
    try:
        subprocess.run(["make", "-C", "indexer"])
    except subprocess.CalledProcessError:
        print("Failed to compile the indexer")
        exit(1)
    
    # start the crawler
    crawler = WebCrawler(starting_urls, 
                        crawl_limit=CRAWL_LIMIT, 
                        num_workers=NUM_THREADS, 
                        db_config=db)
    crawler.start_crawling()
