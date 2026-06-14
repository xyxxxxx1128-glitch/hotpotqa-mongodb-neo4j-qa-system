from collections.abc import Iterable
from typing import Any

from backend.mongo_client import MongoHotpotClient
from scripts.neo4j_importer import HotpotQANeo4jImporter


class HybridHotpotQAImporter:
    def __init__(self) -> None:
        self.mongo = MongoHotpotClient()
        self.neo4j = HotpotQANeo4jImporter()

    def close(self) -> None:
        self.mongo.close()
        self.neo4j.close()

    def prepare(self, clear: bool) -> None:
        self.mongo.ensure_indexes()
        self.neo4j.create_constraints()
        if clear:
            self.mongo.clear()
            self.neo4j.clear_database()
            self.neo4j.create_constraints()

    def import_items(
        self,
        items: Iterable[dict[str, Any]],
        progress_every: int = 1000,
        include_all_context_sentences: bool = False,
        mongo_batch_size: int = 200,
    ) -> int:
        count = 0
        mongo_batch: list[dict[str, Any]] = []
        neo4j_batch: list[dict[str, Any]] = []

        for item in items:
            mongo_batch.append(item)
            neo4j_batch.append(item)
            count += 1

            if len(mongo_batch) >= mongo_batch_size:
                self.mongo.upsert_many(mongo_batch)
                mongo_batch = []

            if len(neo4j_batch) >= mongo_batch_size:
                self.neo4j.import_items(
                    neo4j_batch,
                    progress_every=0,
                    include_all_context_sentences=include_all_context_sentences,
                )
                neo4j_batch = []

            if progress_every > 0 and count % progress_every == 0:
                print(f"Imported {count} records into MongoDB + Neo4j...")

        if mongo_batch:
            self.mongo.upsert_many(mongo_batch)
        if neo4j_batch:
            self.neo4j.import_items(
                neo4j_batch,
                progress_every=0,
                include_all_context_sentences=include_all_context_sentences,
            )

        return count
