import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
import subprocess
import threading
import time
import random
from queue import Queue
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from database.database import Database
from collections import Counter


class WebCrawler:
    def __init__(self, starting_urls, crawl_limit=1000, num_workers=4, db_config=None, en_only=True):
        self.starting_urls = starting_urls
        self.crawl_limit = crawl_limit
        self.num_workers = num_workers
        self.urls_to_crawl = Queue()
        self.visited_urls = set()
        self.crawl_count = 0
        self.lock = threading.Lock()
        self.stop_crawl = threading.Event()
        self.robots_parsers = {}
        self.db_config = db_config
        self.en_only = en_only

    def create_db_connection(self):
        return Database(self.db_config)

    def extract_url(self, hyperlinks, current_url):
        extracted_urls = []
        for link in hyperlinks:
            href = link.get("href", "")

            # Skip fragment identifiers
            if href.startswith("#"):
                continue

            # Handle protocol-relative URLs
            if href.startswith("//"):
                href = "https:" + href

            # Handle relative URLs
            elif href.startswith("/"):
                base = "{0.scheme}://{0.netloc}".format(urlparse(current_url))
                href = base + href

            # Ignore non-HTTP(S) URLs
            elif not href.startswith("http"):
                continue

            # Strip anchor fragments from the URL
            href = href.split("#")[0]
            extracted_urls.append(href)

        return extracted_urls

    def can_fetch(self, domain, current_url):
        with self.lock:
            if domain not in self.robots_parsers:
                rp = RobotFileParser()
                robots_url = domain + "/robots.txt"
                try:
                    rp.set_url(robots_url)
                    rp.read()
                except Exception:
                    rp = None  # If robots.txt cannot be accessed, assume no restrictions
                self.robots_parsers[domain] = rp

            rp = self.robots_parsers.get(domain)
            return not rp or rp.can_fetch("*", current_url)

    def process_content(self, current_url, content, db_connection):
        webpage_data = {
            "url": current_url,
            "title": BeautifulSoup(content, "html.parser").title.string,
            "text": BeautifulSoup(content, "html.parser").get_text(),
        }

        url_id = db_connection.insert_webpage(webpage_data["url"], webpage_data["title"], webpage_data["text"])

        if not url_id:
            print(f"Failed to get URL ID for: {current_url}")
            return

        # save the data as JSON to pass to the indexer
        json_data = json.dumps(webpage_data)

        try:
            # call the C++ indexer via subprocess
            result = subprocess.run(
                ["./indexer/indexer"],
                input=json_data.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            indexer_result = result.stdout.decode("utf-8")

            data = json.loads(indexer_result)
            print("Inserting word frequencies into the database...")
            frequency_data = data.get('word_frequencies')
            print(frequency_data)
            if frequency_data:
                db_connection.insert_word_frequencies(url_id, frequency_data)

        except subprocess.CalledProcessError as e:
            print(f"Indexer failed: {e.stderr.decode('utf-8')}")

    def crawl(self):
        db_connection = self.create_db_connection()
        while not self.stop_crawl.is_set():
            try:
                current_url = self.urls_to_crawl.get(timeout=5)
                print("Crawling: " + current_url)
            except Exception:
                break

            with self.lock:
                if self.crawl_count >= self.crawl_limit:
                    self.urls_to_crawl.queue.clear()
                    print("Crawl limit reached")
                    self.stop_crawl.set()
                    break
                if current_url in self.visited_urls:
                    self.urls_to_crawl.task_done()
                    continue
                self.visited_urls.add(current_url)

            domain = "{0.scheme}://{0.netloc}".format(urlparse(current_url))

            if not self.can_fetch(domain, current_url):
                print(f"Access denied by robots.txt: {current_url}")
                self.urls_to_crawl.task_done()
                continue

            time.sleep(random.uniform(2, 5))
            try:
                response = requests.get(current_url, timeout=5)
                response.raise_for_status()  # Check for request errors

                if not self._is_english(response, response.content):
                    print(f"Skipping non-English page: {current_url}")
                    self.urls_to_crawl.task_done()
                    continue

                content = response.content
                self.process_content(current_url, content, db_connection)

                webpage = BeautifulSoup(content, "html.parser")

                print(f"Title: {webpage.title.string}")
                print(f"URL: {current_url}")
                print(f"Content length: {len(content)}")
                print(f"Total Links Found: {len(webpage.find_all('a'))}")
                print("--------------------------------------------")

                hyperlinks = webpage.select("a[href]")
                new_urls = self.extract_url(hyperlinks, current_url)

                with self.lock:
                    for new_url in new_urls:
                        if new_url not in self.visited_urls:
                            self.urls_to_crawl.put(new_url)
                            
                            from_url_id = db_connection.get_url_id(current_url)
                            to_url_id = db_connection.get_url_id(new_url)

                            if from_url_id and to_url_id:
                                db_connection.insert_backlink(from_url_id, to_url_id)
                                
                    self.crawl_count += 1

            except requests.RequestException as e:
                print(f"Failed to fetch {current_url}: {e}")
            finally:
                self.urls_to_crawl.task_done()

        db_connection.close()

    def start_crawling(self):
        for seed_url in self.starting_urls:
            self.urls_to_crawl.put(seed_url)

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for _ in range(self.num_workers):
                executor.submit(self.crawl)

        print("All URLs have been crawled")
    

    def _is_english(self, response, content):
        if 'Content-Language' in response.headers:
            if 'en' in response.headers['Content-Language'].lower():
                return True

        soup = BeautifulSoup(content, "html.parser")
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang', '').startswith('en'):
            return True

        return False

