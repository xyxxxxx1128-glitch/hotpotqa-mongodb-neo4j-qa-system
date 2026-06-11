import argparse

from datasets import load_dataset

from scripts.neo4j_importer import HotpotQANeo4jImporter


def main() -> None:
    parser = argparse.ArgumentParser(description="Import HotpotQA records into Neo4j.")
    parser.add_argument("--split", default="train", help="Dataset split, default: train")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum records to import")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all Neo4j nodes and relationships before importing",
    )
    args = parser.parse_args()

    dataset = load_dataset("hotpotqa/hotpot_qa", "distractor", split=args.split)
    rows = [dict(item) for item in dataset.select(range(min(args.limit, len(dataset))))]

    importer = HotpotQANeo4jImporter()
    try:
        importer.create_constraints()
        if args.clear:
            importer.clear_database()
            importer.create_constraints()
        importer.import_items(rows)
        print(f"Imported {len(rows)} HotpotQA records into Neo4j.")
    finally:
        importer.close()


if __name__ == "__main__":
    main()
