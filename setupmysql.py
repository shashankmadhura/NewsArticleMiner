# automate_mysql_script.py

import mysql.connector
from dotenv import load_dotenv
import os

# load dot env
load_dotenv()

# Database connection configuration
db_config = {
    'user': 'root',
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST')
}

# Connect to MySQL server to execute the GRANT statement
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    print("GRANT statement executed successfully.")

except mysql.connector.Error as error:
    print("Error executing GRANT statement:", error)

finally:
    # Close connection
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()

# SQL statements for creating database and tables
create_statements = [
    """
    CREATE USER 'user1'@'%' IDENTIFIED WITH mysql_native_password BY '1234';
    """,
    """
    GRANT ALL PRIVILEGES ON *.* TO 'user1'@'%';
    """,
    """
    FLUSH PRIVILEGES;
    """,
    """
    CREATE DATABASE IF NOT EXISTS scraped_news_articles;
    """,
    """
    USE scraped_news_articles;
    """,
    """
    CREATE TABLE IF NOT EXISTS publishers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        website VARCHAR(255)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS articles (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(1000),
        text LONGTEXT,
        html LONGTEXT,
        published_date DATETIME,
        source_url VARCHAR(1000),
        canonical_link VARCHAR(1000),
        meta_data JSON,
        meta_description TEXT, 
        meta_keywords VARCHAR(1000),
        publisher_id INT,
        FOREIGN KEY (publisher_id) REFERENCES publishers(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS authors (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS article_authors (
        article_id INT,
        author_id INT,
        PRIMARY KEY (article_id, author_id),
        FOREIGN KEY (article_id) REFERENCES articles(id),
        FOREIGN KEY (author_id) REFERENCES authors(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS hourly_summary (
        id INT AUTO_INCREMENT PRIMARY KEY,
        publisher_id INT,
        publication_hour DATETIME,
        article_count INT,
        FOREIGN KEY (publisher_id) REFERENCES publishers(id)
    )
    """
]

# Connect to MySQL server
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    print("Connected to MySQL server.")

    # Execute each create statement
    for create_statement in create_statements:
        cursor.execute(create_statement)

    # Commit the changes
    connection.commit()

    print("Database and tables created successfully.")

except mysql.connector.Error as error:
    print("Error creating database and tables:", error)

finally:
    # Close connection
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
