#!/usr/bin/env python3
import sys
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

def main():
    if len(sys.argv) != 3:
        print("Usage: python render_pair.py docA.json docB.json", file=sys.stderr)
        sys.exit(1)

    docA_file, docB_file = sys.argv[1], sys.argv[2]

    # Load docs
    with open(docA_file, "r", encoding="utf-8") as f:
        docA = json.load(f)
    with open(docB_file, "r", encoding="utf-8") as f:
        docB = json.load(f)

    # Jinja environment
    env = Environment(
        loader=FileSystemLoader("."),  # template must be in current folder
        autoescape=select_autoescape(enabled_extensions=("html", "j2"))
    )
    tpl = env.get_template("pair_panels.html.j2")

    # Render HTML
    html_str = tpl.render(a=docA, b=docB)

    # Write preview
    with open("preview_pair.html", "w", encoding="utf-8") as f:
        f.write(html_str)

    print("Wrote preview_pair.html")

if __name__ == "__main__":
    main()