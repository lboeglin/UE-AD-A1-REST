import json
import os

from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://root:example@localhost:27017/")
DATABASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases")

client = MongoClient(MONGO_URL)
db = client["user"]

def init_collection(name):
    """Returns the collection, filled from databases/<name>.json the first time."""
    collection = db[name]
    if collection.count_documents({}) == 0:
        with open(os.path.join(DATABASES_DIR, f"{name}.json"), "r") as jsf:
            collection.insert_many(json.load(jsf)[name])
    return collection
