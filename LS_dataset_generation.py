from utils import build_instances_keys_dict, replace_with_full_entries
from pairing import build_pairs
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uuid
import copy
import json
import random


def fix_galaxy_links(doc):
    """
    Replace 'galaxy.bi.uni-freiburg.de/tool_runner?' with 'https://usegalaxy.eu/root?' in data.webpage links.
    """
    new_links = []
    if doc.get('data') and doc['data'].get('webpage'):
        for link in doc['data']['webpage']:
            new_links.append(link.replace(
                "https://galaxy.bi.uni-freiburg.de/tool_runner?", 
                "https://usegalaxy.eu/root?"
            ))
        doc['data']['webpage'] = new_links
    return doc


def get_html_for_pair(itemA, itemB):
    env = Environment(
        loader=FileSystemLoader("."),  # template must be in current folder
        autoescape=select_autoescape(enabled_extensions=("html", "j2"))
    )
    tpl = env.get_template("pair_panels.html.j2")
    return tpl.render(a=itemA, b=itemB)


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

        # build_disambiguation_pairs - merge occurs here
        conflict_pairs, _ = build_pairs(copy.deepcopy(conflict_full), key, more_than_two_pairs=0)

        for conflict_pair in conflict_pairs:
            itemA = conflict_pair["disconnected"][0]
            itemB = conflict_pair["remaining"][0]
            pairs[key] = [itemA, itemB]
            # If multiple pairs per conflict_id could exist and you need all, adapt structure accordingly.

    return pairs


if __name__ == "__main__":
    # 18 annotators (full roster)
    annotators = [
        "Marie Curie",
        "Rosalind Franklin",
        "Chien-Shiung Wu",
        "Katherine Johnson",
        "Dorothy Hodgkin",
        "Barbara McClintock",
        "Vera Rubin",
        "Sally Ride",
        "Sofia Kovalevskaya",  # (Sophia)
        "Rachel Carson",
        "Margarita Salas",
        "Emmy Noether",
        "Ada Lovelace",
        "Florence Nightingale",
        "Hedy Lamarr",
        "Tu Youyou",
        "Rita Levi-Montalcini",
        "Mae Jemison",
    ]

    # For reproducibility, optionally set a seed:
    # random.seed(42)

    with open("data/conflict_blocks_0.3.json","r", encoding="utf-8") as infile:
        conflict_blocks = json.load(infile)

    # Build only 30 randomly selected pairs
    pairs = build_final_pairs(conflict_blocks, sample_size=30)

    
    n = 0
    tasks = []
    for pair_id, (rawA, rawB) in pairs.items():
        
        # Fix links before rendering HTML
        itemA = fix_galaxy_links(rawA)
        itemB = fix_galaxy_links(rawB)

        html = get_html_for_pair(itemA, itemB)

        # Every annotator annotates this pair
        tasks.append({
            "id": str(uuid.uuid4()),
            "data": {
                "conflict_id": pair_id,
                "html": html
            }
        })
        

    with open('tasks_30.json', "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
        
