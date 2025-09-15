#!/usr/bin/env python3
import sys, json, uuid
from collections import Counter

def assign_annotators(pairs, annotators, k=3):
    n = len(annotators)
    if n < k:
        raise ValueError(f"Need at least {k} annotators, got {n}")
    return {pair: [annotators[(i + j) % n] for j in range(k)]
            for i, pair in enumerate(pairs)}

def get_html_for_pair(pair_id):
    """Stub: replace with real HTML render/load"""
    return f"<div><strong>{pair_id}</strong>: (A/B HTML goes here)</div>"

def build_array_tasks(pairs, annotators, k=3):
    mapping = assign_annotators(pairs, annotators, k=k)
    tasks = []
    for pair_id, team in mapping.items():
        html = get_html_for_pair(pair_id)
        for ann in team:
            tasks.append({
                "id": str(uuid.uuid4()),
                "data": {
                    "pair_id": pair_id,
                    "annotator": ann,
                    "html": html
                }
            })
    return tasks

if __name__ == "__main__":
    pairs = [f"pair-{i:03d}" for i in range(1, 6)]  # example: 5 pairs
    
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
    tasks = build_array_tasks(pairs, annotators, k=3)

    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    # quick sanity check
    load = Counter(t["data"]["annotator"] for t in tasks)
    print("Per-annotator load:", dict(load))
    print("Wrote tasks.json")