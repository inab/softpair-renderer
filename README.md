# Pair Renderer for Label Studio

This small utility builds side-by-side HTML panels from two software metadata documents (e.g., BioConda, bio.tools, Galaxy metadata) so they can be annotated in Label Studio.

The goal is to help human annotators decide whether two records refer to the same software.



## What it does
-	Takes two JSON “tool docs” shaped like the metadata in our pipeline.
-	Uses a Jinja2 template (`pair_panels.html.j2`) to render each doc into a clean HTML panel (“A” and “B”).
-	Adds inline styles so the HTML renders reliably inside Label Studio.
-	Supports common fields: name, source, version, labels, repository, webpage, download, documentation, authors, license, description, input, output, etc.
-	Handles missing/optional fields gracefully.



## How to render
	
 1.	Place your two JSON docs on disk, e.g. `docA.json` and `docB.json`.
 2.	Run the renderer script: 
    ```python
    python render_pair.py docA.json docB.json
    ```
This will output the combined HTML to `preview_pair.html`.



## Using in Label Studio

1.	In your [Label Studio](https://labelstudio-inb.bsc.es) project, set the labeling interface config to something like the content of `labelstudio_config.html`. 

2. Import the HTML file (`preview_pair.html`) in LabelStudio.

2.	Annotators will see two panels (A and B) and answer whether they are the same software.
![alt text](image-1.png)
