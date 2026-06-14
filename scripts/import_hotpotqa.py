import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from datasets import Dataset, load_dataset

from scripts.hybrid_importer import HybridHotpotQAImporter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import HotpotQA records into MongoDB and Neo4j."
    )
    parser.add_argument("--split", default="train", help="Dataset split, default: train")
    parser.add_argument(
        "--data-file",
        default=None,
        help="Optional local .json/.jsonl/.parquet file. Use this when Hugging Face Hub is not reachable.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum records to import. Omit this option to import the full split.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1000,
        help="Print progress every N records. Use 0 to disable progress logs.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all Neo4j nodes and relationships before importing",
    )
    parser.add_argument(
        "--include-all-context",
        action="store_true",
        help=(
            "Import every context sentence into Neo4j. By default only supporting "
            "fact sentences are imported to keep the graph compact."
        ),
    )
    parser.add_argument(
        "--mongo-batch-size",
        type=int,
        default=200,
        help="Number of MongoDB documents to upsert per batch.",
    )
    args = parser.parse_args()

    dataset = load_hotpotqa_dataset(args)
    total = len(dataset) if args.limit is None else min(args.limit, len(dataset))
    rows = (dict(dataset[index]) for index in range(total))

    importer = HybridHotpotQAImporter()
    try:
        importer.prepare(clear=args.clear)
        count = importer.import_items(
            rows,
            progress_every=args.progress_every,
            include_all_context_sentences=args.include_all_context,
            mongo_batch_size=args.mongo_batch_size,
        )
        print(
            f"Imported {count} HotpotQA records from split '{args.split}' "
            "into MongoDB and Neo4j."
        )
    finally:
        importer.close()


def load_hotpotqa_dataset(args: argparse.Namespace) -> Dataset:
    if args.data_file:
        data_file = Path(args.data_file).expanduser().resolve()
        if not data_file.exists():
            raise FileNotFoundError(f"Local data file does not exist: {data_file}")
        suffix = data_file.suffix.lower()
        if suffix in {".json", ".jsonl"}:
            return load_dataset("json", data_files=str(data_file), split="train")
        if suffix == ".parquet":
            return load_dataset("parquet", data_files=str(data_file), split="train")
        raise ValueError("Only .json, .jsonl and .parquet local files are supported.")

    try:
        return load_dataset("hotpotqa/hotpot_qa", "distractor", split=args.split)
    except FileNotFoundError as exc:
        raise SystemExit(
            "\nFailed to download HotpotQA from Hugging Face.\n"
            "This usually means the current network cannot reach Hugging Face, "
            "or the dataset has not been cached locally.\n\n"
            "Options:\n"
            "1. Check your network/proxy, then rerun the same command.\n"
            "2. Download the HotpotQA parquet/json file manually and rerun with:\n"
            "   python scripts/import_hotpotqa.py --data-file path\\to\\file.parquet --limit 10000 --clear\n"
        ) from exc


if __name__ == "__main__":
    main()
