from os import getenv
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection

# Load environment variables from .env
load_dotenv()


class MongoConnection:
    """
    Central MongoDB connection wrapper.
    Exposes typed collections AND safe dynamic access.
    """

    def __init__(self) -> None:
        uri = getenv("MONGODB_URI")
        db_name = getenv("MONGODB_DB")

        if not uri or not db_name:
            raise RuntimeError(
                "Environment variables MONGODB_URI and MONGODB_DB are required."
            )

        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]

        # ---- Typed collections ----
        self.vehicles: Collection = self.db["vehicles"]
        self.telemetry: Collection = self.db["telemetry"]
        self.predictions: Collection = self.db["predictions"]
        self.risk_logs: Collection = self.db["risk_logs"]
        self.maintenance_events: Collection = self.db["maintenance_events"]
        self.agent_actions: Collection = self.db["agent_actions"]
        self.feedback: Collection = self.db["feedback"]
        self.alerts: Collection = self.db["alerts"]
        self.agent_timeline: Collection = self.db["agent_timeline"]
        self.maintenance_recommendations: Collection = self.db["maintenance_recommendations"]
        # newly added collections for RBAC and assistance features
        self.users: Collection = self.db["users"]
        self.service_centers: Collection = self.db["service_centers"]

    # ---- Health check ----
    def ping_db(self) -> str:
        self.client.admin.command("ping")
        return "MongoDB connection successful"

    # ---- SAFE dynamic collection access ----
    def get_collection(self, name: str) -> Collection:
        if not hasattr(self, name):
            raise AttributeError(
                f"Collection '{name}' is not defined in MongoConnection"
            )
        return getattr(self, name)

    # ---- Generic helpers ----
    def insert(self, collection: str, document: dict):
        return self.get_collection(collection).insert_one(document)

    def find_one(self, collection: str, query: dict, sort: list | None = None):
        return self.get_collection(collection).find_one(query, sort=sort)

    def find(self, collection: str, query: dict):
        return list(self.get_collection(collection).find(query))

    def find_many(self, collection: str, query: dict, limit: int = 100):
        cursor = (
            self.get_collection(collection)
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
        return list(cursor)

    def update_one(self, collection: str, query: dict, update: dict):
        return self.get_collection(collection).update_one(query, update, upsert=False)

    def upsert_one(self, collection: str, query: dict, update: dict):
        return self.get_collection(collection).update_one(query, update, upsert=True)

    def delete_one(self, collection: str, query: dict):
        return self.get_collection(collection).delete_one(query)
