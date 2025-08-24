from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Explicitly load the .env from project root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "pathfinder")

print("Using Mongo URI:", MONGO_URI)  # Debugging
print("Using Mongo DB:", MONGO_DB)    # Debugging

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
