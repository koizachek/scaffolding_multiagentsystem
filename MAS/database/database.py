import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()

_uri = f"mongodb+srv://kristianschwarz:{os.environ['DB_PASSWORD']}@mas.oxzqvr2.mongodb.net/?retryWrites=true&w=majority&appName=MAS"


def _start_client():
    try:
        return MongoClient(_uri, timeoutMS=1000)
    except Exception as e:
        raise Exception("Failed to reach MongoDB cluster and start the client: ", e)


def ping():
    client = _start_client()
    try:
        client = _start_client()
        client.admin.command("ping")
        print("Client pinged the server!")
    except Exception as e:
        raise Exception ("Failed to ping server with client: ", e)


if __name__ == "__main__":
    ping()

