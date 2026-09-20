import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()


MONGODB_URI = os.getenv("MONGODB_URI")


if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing from the .env file."
    )


client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi(
        "1",
        strict=True,
        deprecation_errors=True
    )
)


db = client["felix"]


def get_database():
    """
    Return the FELIX MongoDB database.
    """
    return db