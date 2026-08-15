import os

import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rideguard360")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not set in .env")

client = pymongo.AsyncMongoClient(MONGODB_URI)

db = client[DATABASE_NAME]


async def connect_to_mongodb():
    await client.admin.command("ping")
    print("✅ MongoDB connected successfully")


async def close_mongodb_connection():
    await client.close()
    print("🔴 MongoDB connection closed")