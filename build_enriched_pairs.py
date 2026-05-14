"""
Build and persist the full set of enriched software-identity pairs.

Reads every conflict in the input file, fetches complete metadata from MongoDB,
runs the pair-building logic, and writes the result to a timestamped JSON file.

Both the manual-annotation pipeline (LS_dataset_generation.py) and the automated
disambiguation pipeline must load pairs from the file produced here instead of
hitting the database at task-preparation time.

Usage:
    python build_enriched_pairs.py \
        --conflicts data/conflicts.20260421T111602Z-8d84134d-manual_group_correction.json \
        --output data/enriched_pairs.json
"""

import argparse
import copy
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from bson import json_util

from pairing import build_pairs
from utils import replace_with_full_entries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_all_enriched_pairs(conflict_blocks: dict) -> dict:
    """
    Enrich every conflict in *conflict_blocks* and expand into final pairs.

    Returns:
        {pair_id: [itemA, itemB]}  — one entry per pair, covering all conflicts.
    """
    pairs: dict = {}
    total = len(conflict_blocks)

    for idx, (key, conflict) in enumerate(conflict_blocks.items(), start=1):
        logger.info(f"[{idx}/{total}] Processing conflict: {key}")

        try:
            conflict_full = replace_with_full_entries(conflict, instances_dict=None)
        except Exception as exc:
            logger.warning(f"  Skipping {key}: could not enrich entries — {exc}")
            continue

        conflict_pairs, _ = build_pairs(
            copy.deepcopy(conflict_full),
            key,
            more_than_two_pairs=0,
        )

        if not conflict_pairs:
            logger.info(f"  No pairs produced for {key}, skipping.")
            continue

        for i, conflict_pair in enumerate(conflict_pairs):
            item_a = conflict_pair["disconnected"][0]
            item_b = conflict_pair["remaining"][0]

            pair_id = key if len(conflict_pairs) == 1 else f"{key}__pair_{i + 1}"
            pairs[pair_id] = [item_a, item_b]

    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="Build enriched software-identity pairs from conflict blocks.")
    parser.add_argument(
        "--conflicts",
        default="data/conflicts.20260421T111602Z-8d84134d-manual_group_correction.json",
        help="Path to the conflict-blocks JSON file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Path for the output JSON file. "
            "Defaults to data/enriched_pairs.<timestamp>.json."
        ),
    )
    args = parser.parse_args()

    conflicts_path = Path(args.conflicts)
    if not conflicts_path.exists():
        logger.error(f"Conflicts file not found: {conflicts_path}")
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = Path(args.output) if args.output else Path(f"data/enriched_pairs.{timestamp}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading conflicts from {conflicts_path}")
    with conflicts_path.open("r", encoding="utf-8") as fh:
        conflict_blocks = json.load(fh)
    logger.info(f"Loaded {len(conflict_blocks)} conflict blocks.")

    pairs = build_all_enriched_pairs(conflict_blocks)

    logger.info(f"Built {len(pairs)} pairs from {len(conflict_blocks)} conflicts.")
    logger.info(f"Writing pairs to {output_path}")

    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(pairs, fh, ensure_ascii=False, indent=2, default=json_util.default)

    logger.info("Done.")


if __name__ == "__main__":
    main()
