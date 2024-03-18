from logging.handlers import RotatingFileHandler
from newspaper import Article, Config
import mysql.connector.pooling
import os, time, json, logging, feedparser, argparse
import datetime as dt
from scheduler import Scheduler
from dotenv import load_dotenv

# load dot env
load_dotenv()

# Initialize argument parser
parser = argparse.ArgumentParser(description="Run a news scraper")

# Add command line arguments
parser.add_argument("--rss_url", type=str, default="https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en", help="RSS URL for news feed")
parser.add_argument("--interval", type=int, default=15, help="Interval in minutes for running the scraper")

# Parse command line arguments
args = parser.parse_args()

# Access the values
rss_url = args.rss_url

# Run scraper every 15 minute
# The value is in minute
run_pipeline_interval = args.interval


# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Create the 'logs' directory if it doesn't exist
logs_directory = os.path.join(current_directory, 'logs')
os.makedirs(logs_directory, exist_ok=True)

# Configure logging with line numbers
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = os.path.join(logs_directory, 'scraping.log')
handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')  # Include line numbers
handler.setFormatter(formatter)
logger.addHandler(handler)


# MySQL connection pooling configuration
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **db_config)

logger.info("Connected to MySQL")

## Initialize the database connection outside of the functions
connection = pool.get_connection()


# Parse the rss feed
def parse_rss(rss_url):
    try:
        feed = feedparser.parse(rss_url)
        article_urls = [entry.link for entry in feed.entries]
        return article_urls
    except Exception as e:
        logger.error(f"Error parsing RSS feed: {e}")
        return []

# Check article exists in db or not
def article_exists(cursor, url):
    try:
        # Check if an article with the given URL and publish date already exists in the database
        query = "SELECT COUNT(*) FROM articles WHERE source_url = %s"
        cursor.execute(query, (url,))
        count = cursor.fetchone()[0]

        if count > 0:
            logger.info("Skipping the article: Already exists")

        return count > 0
    except Exception as e:
        logger.error(f"Error checking if article exists: {e}")
        return False

# Scrape the articles
def scrape_article(cursor, url):
    try:
        config = Config()

        # To include binary data while scraping
        # Almost all the article contains binary data
        # If set to false, throws exception if article has binary data
        config.allow_binary_content = True

        article = Article(url, config=config)
        article.download()
        article.parse()
        if article.download_exception_msg:
            logger.error("Error downloading the article", article.download_exception_msg)
            return None
            
        return {
            'title': article.title,
            'text': article.text_cleaned,
            'authors': article.authors,
            'published_date': article.publish_date,
            'source_url': article.original_url,
            'canonical_link': article.canonical_link,
            'meta_data': article.meta_data,
            'meta_keywords': article.meta_keywords,
            'meta_description': article.meta_description,
            'html': article.article_html,
            'publisher': article.meta_site_name,
        }
    except Exception as e:
        logger.error(f"Error scraping article from {url}: {e}")
        return None

# Insert the article data into articles table
def insert_article_data(cursor, data):
    try:
        # Assuming data['meta_keywords'] is a list
        meta_keywords_json = json.dumps(data['meta_keywords'])

        insert_article_query = """
            INSERT INTO articles 
            (title, text, html, published_date, source_url, canonical_link, meta_data, meta_keywords, meta_description) 
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_article_query, (
            data['title'], data['text'], data['html'], data['published_date'], data['source_url'],
            data['canonical_link'], json.dumps(data['meta_data']), meta_keywords_json, data['meta_description']
        ))

        article_id = cursor.lastrowid

        # Insert authors into the authors table
        for author in data['authors']:
            # Check if author already exists
            select_author_query = "SELECT id FROM authors WHERE name = %s"
            cursor.execute(select_author_query, (author,))
            result = cursor.fetchone()
            if result:
                author_id = result[0]
            else:
                insert_author_query = "INSERT INTO authors (name) VALUES (%s)"
                cursor.execute(insert_author_query, (author,))
                author_id = cursor.lastrowid

            # Insert into article_authors table
            insert_article_author_query = "INSERT INTO article_authors (article_id, author_id) VALUES (%s, %s)"
            cursor.execute(insert_article_author_query, (article_id, author_id))

        # Insert publisher into publishers table
        publisher = data['publisher']
        # Check if publisher already exists
        select_publisher_query = "SELECT id FROM publishers WHERE name = %s"
        cursor.execute(select_publisher_query, (publisher,))
        result = cursor.fetchone()
        if result:
            publisher_id = result[0]
        else:
            insert_publisher_query = "INSERT INTO publishers (name) VALUES (%s)"
            cursor.execute(insert_publisher_query, (publisher,))
            publisher_id = cursor.lastrowid

        # Update article record with publisher_id
        update_article_query = "UPDATE articles SET publisher_id = %s WHERE id = %s"
        cursor.execute(update_article_query, (publisher_id, article_id))

        # Update hourly summary
        update_hourly_summary(cursor, publisher_id, data['published_date'])

    except Exception as e:
        logger.error(f"Error inserting data into database: {e}")

# Function to update hourly summary
def update_hourly_summary(cursor, publisher_id, publication_date):
    try:
        # Your logic to update the hourly summary table goes here
        pass
    except Exception as e:
        logger.error(f"Error updating hourly summary: {e}")

# Function to run the pipeline
def run_pipeline(cursor):
    try:
        article_urls = parse_rss(rss_url)
        count = 0
        for url in article_urls:
            if not article_exists(cursor, url):
                scraped_data = scrape_article(cursor, url)
                if scraped_data:
                    insert_article_data(cursor, scraped_data)
                    count += 1
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")

run_pipeline()

# Initialize the scheduler
schedule = Scheduler()
schedule.cyclic(dt.timedelta(minutes=run_pipeline_interval), run_pipeline, args=[connection.cursor()]) 

# Run the scheduler continuously
while True:
    schedule.exec_jobs()
    time.sleep(1)