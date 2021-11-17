from pymongo import MongoClient
from urllib.parse import quote_plus
import os


class PermanentRepository:

    client: MongoClient = MongoClient(
        f"mongodb://{quote_plus(os.environ['DB_ADMIN_USER'])}:{quote_plus(os.environ['DB_ADMIN_PASSWD'])}@199.231.189.38:27017/admin"
    )
    permanent_db = client["permanent"]

    # collections
    suffixes = permanent_db.get_collection("suffixes")
    prefixes = permanent_db.get_collection("prefixes")
    checked_domains = permanent_db.get_collection("checked_domains")