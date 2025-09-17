# Pair renderer for Label Studio

This utility builds side-by-side HTML panels from two software metadata documents (e.g., BioConda, bio.tools, Galaxy metadata) so they can be annotated in [Label Studio](https://labelstudio-inb.bsc.es).

The goal is to help human annotators decide whether two records refer to the same software.


## What it currently does

- Loads candidate conflict pairs from `conflict_blocks.json` (produced by the Software Observatory pipeline).
- Expands each entry to its full metadata (via `utils.build_instances_keys_dict` and `replace_with_full_entries`).
- Builds disambiguation pairs with `pairing.build_pairs`.
- Applies fixes to metadata (e.g. replaces old Galaxy links with https://usegalaxy.eu/root?).
- Renders each pair into a clean HTML panel using the Jinja2 template `pair_panels.html.j2`.
- Assigns 3 annotators per pair, cycling evenly through a list of historical scientists.
- Produces a JSON file with all tasks for Label Studio.

## How to run 

 1.	Ensure your environment has the dependencies installed:

    ```bash
    pip install -r requirements.txt
    ```

 2. Prepare your input file (example: `data/conflict_blocks_test.json`). 
 3. Run the script:
    ```bash
    python LS_dataset_generation.py
    ```
 4. The script will generate:
    - `test_tasks.json` → tasks in JSON array format, ready for Label Studio import.

## Label Studio setup

 1.	In your Label Studio project, set the labeling interface to the config provided in `labelstudio_config.html`.
	•	This config asks: *“Are A and B the same software?”*
	•	It provides choices: **Yes / No / Unsure**, plus an optional notes box.
 
 2.	Import test_tasks.json. Each task contains:
	•	`conflict_id` → unique ID of the conflict.
	•	`annotator` → name of the assigned annotator.
	•	`html` → the rendered HTML panels.
 
 3.	Annotators will see two panels (A and B), can navigate links, and record their judgment.

## Output example

Each task in `test_tasks.json` looks like:

```json
{
  "id": "f6a24b9e-1234-4e7c-a89b-9db8fa04aabb",
  "data": {
    "conflict_id": "block-42",
    "annotator": "Rosalind Franklin",
    "html": "<div>…rendered HTML for pair A/B…</div>"
  }
}
```