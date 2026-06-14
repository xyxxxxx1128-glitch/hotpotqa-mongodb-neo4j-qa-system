import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.mongo_client import mongo_client
from backend.neo4j_client import neo4j_client


def main() -> None:
    mongo_count = mongo_client.collection.count_documents({})
    node_counts = neo4j_client.run(
        """
        MATCH (n)
        UNWIND labels(n) AS label
        RETURN label, count(*) AS count
        ORDER BY label
        """
    )
    relationship_counts = neo4j_client.run(
        """
        MATCH ()-[r]->()
        RETURN type(r) AS relationship, count(*) AS count
        ORDER BY relationship
        """
    )
    question_counts = neo4j_client.run(
        """
        MATCH (q:Question)
        RETURN count(q) AS questions,
               count(DISTINCT q.type) AS types,
               count(DISTINCT q.level) AS levels
        """
    )

    print("MongoDB summary")
    print({"documents": mongo_count})

    print("\nNeo4j question summary")
    for row in question_counts:
        print(row)

    print("\nNode counts")
    for row in node_counts:
        print(row)

    print("\nRelationship counts")
    for row in relationship_counts:
        print(row)


if __name__ == "__main__":
    main()
