from utils import build_instances_keys_dict, replace_with_full_entries
from pairing import build_pairs
from jinja2 import Environment, FileSystemLoader, select_autoescape
import uuid
import copy
import json

def fix_galaxy_links(doc):
    """
    Recursively traverse dict/list/str and replace
    'galaxy.bi.uni-freiburg.de/tool_runner?' with 'https://usegalaxy.eu/root?'.
    """
    print(doc)
    new_links = []
    if doc['data'].get('webpage'):
        for link in doc['data'].get('webpage'):
            new_links.append(link.replace("https://galaxy.bi.uni-freiburg.de/tool_runner?", "https://usegalaxy.eu/root?"))

        doc['data']['webpage'] = new_links

    return doc


    
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


def build_final_pairs(conflict_blocks):

    instances_dict = build_instances_keys_dict() 
    pairs = {}

    for key in conflict_blocks:
        # replace with full records
        conflict = conflict_blocks[key]
        conflict_full = replace_with_full_entries(conflict, instances_dict) 

        # build_disambiguation_pairs - here is where merge occurs
        conflict_pairs, _ = build_pairs(copy.deepcopy(conflict_full), key, more_than_two_pairs=0) 

        for conflict_pair in conflict_pairs:

            itemA = conflict_pair["disconnected"][0]
            itemB = conflict_pair["remaining"][0]

            pairs[f"{key}"] = [itemA, itemB]

    return pairs

if __name__ == "__main__":

    annotators = [
        "Marie Curie",            # Nobel laureate in Physics & Chemistry, pioneer of radioactivity
        "Rosalind Franklin",      # Crystallographer whose data was key to discovering DNA structure
        "Chien-Shiung Wu",        # Experimental physicist, worked on beta decay
        "Katherine Johnson",      # NASA mathematician, critical to spaceflight calculations
        "Dorothy Hodgkin",        # Nobel laureate in Chemistry, advanced protein crystallography
        "Barbara McClintock",     # Nobel laureate in Medicine, discovered transposons
        "Vera Rubin",             # Astronomer who provided evidence for dark matter
        "Sally Ride",             # Physicist and first American woman in space
        "Sophia Kovalevskaya",    # Mathematician, pioneer for women in mathematics
        "Rachel Carson",          # Marine biologist, author of *Silent Spring*
        "Margarita Salas",        # Spanish biochemist, pioneer in molecular biology
        "Emmy Noether",           # Mathematician, founder of modern abstract algebra
    ]

    with open("data/conflict_blocks_test.json","r") as infile:
        conflict_blocks = json.load(infile)
    
    pairs =  build_final_pairs(conflict_blocks)

    mapping = assign_annotators(pairs, annotators, k=3)

    tasks = []
    for pair_id, team in mapping.items():

        itemA = fix_galaxy_links(pairs[pair_id][0])
        itemB = fix_galaxy_links(pairs[pair_id][1])

        html = get_html_for_pair(pairs[pair_id][0], pairs[pair_id][1])
        for ann in team:
            tasks.append({
                "id": str(uuid.uuid4()),
                "data": {
                    "conflict_id": pair_id,
                    "annotator": ann,
                    "html": html
                }
            })
        

    with open("test_tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
