import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from utils.xml_processor import extract_articles_from_dump

load_dotenv()


def connect_mongo():
    DATABASE_URL = os.getenv("DATABASE_URL").replace(
        "<db_password>", os.getenv("DATABASE_PASSWORD")
    )
    try:
        client = MongoClient(DATABASE_URL)
        db = client["wikipedia"]
        print("Connected to MongoDB.")
        return client, db
    except Exception as e:
        print(f"Error: Could not connect to MongoDB! {e}")
        raise

def save_to_mongodb(db, file_path):
    collection = db["wikipedia_tr"]
    collection.create_index("title", unique=True)

    for article in extract_articles_from_dump(file_path):
        try:
            collection.insert_one(article)
            print(f"Makale kaydedildi: {article['title']}")
        except DuplicateKeyError:
            print(f"Makale zaten var, atlanıyor: {article['title']}")
