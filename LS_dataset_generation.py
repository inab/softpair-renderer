from utils import build_instances_keys_dict, replace_with_full_entries
from pairing import build_pairs
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bson import json_util
import uuid
import copy
import json
import random
import os
import re


def fix_galaxy_links(doc):
    """
    Replace old Galaxy Freiburg tool_runner links with usegalaxy.eu root links.
    """
    new_doc = copy.deepcopy(doc)

    if new_doc.get("data") and new_doc["data"].get("webpage"):
        new_doc["data"]["webpage"] = [
            link.replace(
                "https://galaxy.bi.uni-freiburg.de/tool_runner?",
                "https://usegalaxy.eu/root?"
            )
            for link in new_doc["data"]["webpage"]
        ]

    return new_doc


def get_html_for_pair(itemA, itemB):
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(enabled_extensions=("html", "j2"))
    )
    tpl = env.get_template("pair_panels.html.j2")
    return tpl.render(a=itemA, b=itemB)


def slugify_name(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def build_final_pairs(conflict_blocks, sample_size=30):
    """
    Build {conflict_id: [itemA, itemB]} for a random sample of up to `sample_size` conflicts.
    """
    instances_dict = build_instances_keys_dict()
    pairs = {}

    all_ids = list(conflict_blocks.keys())
    selected_ids = random.sample(all_ids, min(len(all_ids), sample_size))

    for key in selected_ids:
        conflict = conflict_blocks[key]
        conflict_full = replace_with_full_entries(conflict, instances_dict)

        conflict_pairs, _ = build_pairs(
            copy.deepcopy(conflict_full),
            key,
            more_than_two_pairs=0
        )

        for i, conflict_pair in enumerate(conflict_pairs):
            itemA = conflict_pair["disconnected"][0]
            itemB = conflict_pair["remaining"][0]

            pair_id = key if len(conflict_pairs) == 1 else f"{key}__pair_{i + 1}"
            pairs[pair_id] = [itemA, itemB]

    return pairs


def assign_pairs_to_annotators(pairs, annotators, annotators_per_case=2):
    """
    Assign each pair to annotators and keep a tracking manifest.

    Returns:
        tasks_by_annotator: {annotator_name: [Label Studio tasks]}
        tracking_records: flat list with one row per annotator-task assignment
    """
    tasks_by_annotator = {annotator: [] for annotator in annotators}
    task_counts = {annotator: 0 for annotator in annotators}
    tracking_records = {}

    pair_items = list(pairs.items())
    random.shuffle(pair_items)

    for pair_uid, (rawA, rawB) in pair_items:
        selected_annotators = sorted(
            annotators,
            key=lambda annotator: (task_counts[annotator], random.random())
        )[:annotators_per_case]

        itemA = fix_galaxy_links(rawA)
        itemB = fix_galaxy_links(rawB)

        html = get_html_for_pair(itemA, itemB)

        for annotator in selected_annotators:
            task_id = str(uuid.uuid4())

            task = {
                "id": task_id,
                "data": {
                    "pair_uid": pair_uid,
                    "conflict_id": pair_uid.split("__pair_")[0],
                    "annotator": annotator,
                    "html": html
                }
            }

            tasks_by_annotator[annotator].append(task)

            if pair_uid not in tracking_records:
                tracking_records[pair_uid] = {
                    "pair_uid": pair_uid,
                    "conflict_id": pair_uid.split("__pair_")[0],
                    "itemA": itemA,
                    "itemB": itemB,
                    "html": html,
                    "annotators": {}
                }

            tracking_records[pair_uid]["annotators"][annotator] = {
                "task_id": task_id
            }

            task_counts[annotator] += 1

    return tasks_by_annotator, list(tracking_records.values())

def write_split_task_files(tasks_by_annotator, output_dir, chunk_size=30):
    """
    Write one or more JSON files per annotator, split into chunks of `chunk_size`.
    """
    os.makedirs(output_dir, exist_ok=True)

    for annotator, tasks in tasks_by_annotator.items():
        annotator_slug = slugify_name(annotator)

        for chunk_idx, start in enumerate(range(0, len(tasks), chunk_size), start=1):
            chunk = tasks[start:start + chunk_size]

            filename = f"tasks_{annotator_slug}_part_{chunk_idx:02d}.json"
            path = os.path.join(output_dir, filename)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)

            print(
                f"{annotator}: part {chunk_idx:02d} "
                f"({len(chunk)} tasks) -> {path}"
            )

            
if __name__ == "__main__":
    annotators = [
        "Marie Curie",
        "Rosalind Franklin",
        "Chien-Shiung Wu",
        "Katherine Johnson",
    ]

    SAMPLE_SIZE = 272
    ANNOTATORS_PER_CASE = 2

    # Optional reproducibility
    random.seed(42)

    with open("data/conflicts.20260421T111602Z-8d84134d-manual_group_correction.json", "r", encoding="utf-8") as infile:
        conflict_blocks = json.load(infile)

    pairs = build_final_pairs(conflict_blocks, sample_size=SAMPLE_SIZE)

    tasks_by_annotator, tracking_records = assign_pairs_to_annotators(
        pairs,
        annotators,
        annotators_per_case=ANNOTATORS_PER_CASE
    )

    output_dir = "labelstudio_tasks_by_annotator"

    write_split_task_files(
        tasks_by_annotator,
        output_dir=output_dir,
        chunk_size=30
    )

    with open("labelstudio_pair_assignment_manifest.json", "w", encoding="utf-8") as f:
        json.dump(
            tracking_records,
            f,
            ensure_ascii=False,
            indent=2,
            default=json_util.default
        )

    print(f"Tracking manifest written with {len(tracking_records)} task assignments.")