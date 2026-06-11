import os
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "your_password")
        self.neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
        origins = os.getenv("CORS_ORIGINS", "*")
        self.cors_origins = [item.strip() for item in origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
