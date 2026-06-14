import re
from typing import Any

from pymongo import ASCENDING, MongoClient

from backend.config import get_settings


class MongoHotpotClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = MongoClient(settings.mongodb_uri)
        self.database = self.client[settings.mongodb_database]
        self.collection = self.database[settings.mongodb_collection]

    def close(self) -> None:
        self.client.close()

    def ping(self) -> bool:
        self.client.admin.command("ping")
        return True

    def ensure_indexes(self) -> None:
        self.collection.create_index([("id", ASCENDING)], unique=True)
        self.collection.create_index([("question", ASCENDING)])
        self.collection.create_index([("answer", ASCENDING)])
        self.collection.create_index([("type", ASCENDING)])
        self.collection.create_index([("level", ASCENDING)])

    def clear(self) -> None:
        self.collection.delete_many({})

    def upsert_many(self, items: list[dict[str, Any]]) -> None:
        if not items:
            return
        for item in items:
            normalized = normalize_for_mongo(item)
            self.collection.replace_one(
                {"id": normalized["id"]},
                normalized,
                upsert=True,
            )

    def search(self, keyword: str, limit: int) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if keyword:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            query = {
                "$or": [
                    {"question": pattern},
                    {"answer": pattern},
                    {"type": pattern},
                    {"level": pattern},
                ]
            }
        cursor = (
            self.collection.find(
                query,
                {"_id": 0, "id": 1, "question": 1, "answer": 1, "type": 1, "level": 1},
            )
            .sort("id", ASCENDING)
            .limit(limit)
        )
        return list(cursor)

    def get_question(self, question_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"id": question_id}, {"_id": 0})

    def cluster_counts(self, field: str) -> list[dict[str, Any]]:
        pipeline = [
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "name": {"$ifNull": ["$_id", "unknown"]}, "count": 1}},
            {"$sort": {"count": -1}},
        ]
        return list(self.collection.aggregate(pipeline))


def normalize_for_mongo(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized["id"] = str(normalized.get("id", ""))
    return normalized


mongo_client = MongoHotpotClient()
