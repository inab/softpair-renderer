from utils import build_instances_keys_dict, replace_with_full_entries
from pairing import build_pairs
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uuid
import copy
import json

def get_html_for_pair(itemA, itemB):
    # Jinja environment
    env = Environment(
        loader=FileSystemLoader("."),  # template must be in current folder
        autoescape=select_autoescape(enabled_extensions=("html", "j2"))
    )
    tpl = env.get_template("pair_panels.html.j2")

    # Render HTML
    html_str = tpl.render(a=itemA, b=itemB)
    
    return html_str


def assign_annotators(pairs, annotators, k=3):
    n = len(annotators)
    if n < k:
        raise ValueError(f"Need at least {k} annotators, got {n}")
    return {pair: [annotators[(i + j) % n] for j in range(k)]
            for i, pair in enumerate(pairs)}


def build_final_pairs():

    conflict_blocks = []
    instances_dict = build_instances_keys_dict() 
    pairs = {}

    for key in conflict_blocks:
        # replace with full records
        conflict = conflict_blocks[key]
        conflict_full = replace_with_full_entries(conflict, instances_dict) 

        # build_disambiguation_pairs - here is where merge occurs
        conflict_pairs, _ = build_pairs(copy.deepcopy(conflict_full), key, more_than_two_pairs=0) 

        n = 0
        for conflict_pair in conflict_pairs:

            itemA = conflict_pair["disconnected"][0]
            itemB = conflict_pair["remaining"][0]

            pairs[f"{key}-{n}"] = [itemA, itemB]
            n += 1

    return pairs

if __name__ == "__main__":

    annotators = [
            "Captain Curator",
            "DocuSaurus Rex",
            "Miss Label",
            "Bugsy McTag",
            "Judge JudyJSON",
            "Professor Pairwise",
            "Loopy Looper",
            "MetaData Mike",
            "Alias Arraya",
            "Nina Nullcheck",
        ]

    pairs =  build_final_pairs()

    mapping = assign_annotators(pairs, annotators, k=3)

    tasks = []
    for pair_id, team in mapping.items():
        html = get_html_for_pair(pairs[pair_id][0], pairs[pair_id][1])
        for ann in team:
            tasks.append({
                "id": str(uuid.uuid4()),
                "data": {
                    "pair_id": pair_id,
                    "annotator": ann,
                    "html": html
                }
            })
        

    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
