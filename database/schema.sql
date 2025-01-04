-- Create a new database for your web crawler
CREATE DATABASE web_crawler;

-- Use the created database
USE web_crawler;

-- Create a table to store crawled data
CREATE TABLE webpages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    text LONGTEXT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a table to store word frequencies for indexing
CREATE TABLE word_frequencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url_id INT,
    word VARCHAR(255),
    frequency INT,
    FOREIGN KEY (url_id) REFERENCES webpages(id)
);

-- Create a table to store backlinks between pages
CREATE TABLE backlinks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_url_id INT,
    to_url_id INT,
    FOREIGN KEY (from_url_id) REFERENCES webpages(id),
    FOREIGN KEY (to_url_id) REFERENCES webpages(id)
);

-- Add a column for PageRank in the webpages table
ALTER TABLE webpages ADD COLUMN pagerank FLOAT DEFAULT 1.0;
