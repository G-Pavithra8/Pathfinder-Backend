from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "pathfinder")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[MONGO_DB]

try:
    client.admin.command('ping')
    print("MongoDB connected successfully!")
except Exception as e:
    print("MongoDB connection error:", e)
