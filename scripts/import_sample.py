import json
from pathlib import Path

from scripts.neo4j_importer import HotpotQANeo4jImporter


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = ROOT / "data" / "sample_hotpotqa.json"


def main() -> None:
    items = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    importer = HotpotQANeo4jImporter()
    try:
        importer.create_constraints()
        importer.import_items(items)
        print(f"Imported {len(items)} sample HotpotQA records into Neo4j.")
    finally:
        importer.close()


if __name__ == "__main__":
    main()
