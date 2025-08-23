# db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "pathfinder")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
