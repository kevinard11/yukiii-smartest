from pymongo import MongoClient
import uuid
import logging, os

logger = logging.getLogger(__name__)

client = MongoClient("mongodb://admin:admin123@localhost:27017/")
# mongo_uri = os.getenv("MONGO_URI")
# client = MongoClient(mongo_uri)

db = client["smartest_db"]
collection = db["metrics"]

def get_10_latest_data_smartest():
    document = collection.find(
                    {},  # filter semua
                    {"_id": 0, "smartest_id": 1, "name": 1, "repo_url": 1}
                ).sort("_id", -1).limit(10)
    print(document)
    if document:
        return list(document)
    else:
        return []

def insert_data_microservices(data, repo_url):
    data['smartest_id'] = str(uuid.uuid4())
    data['repo_url'] = repo_url
    # logger.info(data)
    # print(data)

    insert_result = collection.insert_one(data)
    print("Data inserted with ID:", insert_result.inserted_id)
    return data['smartest_id']

def get_data_smartest_by_id(smartest_id):
    document = collection.find_one({"smartest_id": smartest_id})

    return document