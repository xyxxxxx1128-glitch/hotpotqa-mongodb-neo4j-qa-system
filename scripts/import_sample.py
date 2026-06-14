import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.hybrid_importer import HybridHotpotQAImporter


SAMPLE_FILE = ROOT / "data" / "sample_hotpotqa.json"


def main() -> None:
    items = json.loads(SAMPLE_FILE.read_text(encoding="utf-8"))
    importer = HybridHotpotQAImporter()
    try:
        importer.prepare(clear=True)
        count = importer.import_items(
            items,
            progress_every=0,
            include_all_context_sentences=False,
        )
        print(f"Imported {count} sample HotpotQA records into MongoDB and Neo4j.")
    finally:
        importer.close()


if __name__ == "__main__":
    main()
