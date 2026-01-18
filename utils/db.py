# utils/db.py

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "new_lp")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# ✅ Canonical problems collection
problems_master = db["problems_master"]

# ✅ User-scoped solved collection factory
def user_solved_col(username: str):
    safe = username.lower().replace("-", "_")
    return db[f"user_{safe}_solved"]
