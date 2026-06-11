from typing import Any

from neo4j import GraphDatabase

from backend.config import get_settings


class Neo4jClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.database = settings.neo4j_database
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def close(self) -> None:
        self.driver.close()

    def run(self, query: str, **params: Any) -> list[dict[str, Any]]:
        with self.driver.session(database=self.database) as session:
            result = session.run(query, **params)
            return [record.data() for record in result]


neo4j_client = Neo4jClient()
