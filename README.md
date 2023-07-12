# EasyDiffuion Image Viewer

This program allows for easily viewing of your generated images.

# How to use

You have to first ingest the data into a database to make it possible to search the images. This is done by executing
```
python ingest.py <path>
```
where <path> represents the auto-save location in the webui. You should be aware that at the moment only images that were generated with the metadata format "txt" are detected.

Now you can search for images like this:

```
python -i search.py
# opens search.py in interactive mode, you can now run python commands directly
search_to_html("<query>")
```

The search_to_html command then creates a resultsite.html file that can then be opened with the webbrowser of your choice.
The <query> in search_to_html is an SQL WHERE clause in a table with the columns: path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction

Examples:

```
"width = '512' AND height = '512'"
"prompt like '%astronaut%'"
"model like '%sd%'"
```

# Moving

In case you want to move the installation you'll have to re-ingest the data.

# Roadmap

- [X] ingest json format too
- [X] check if file already ingested
- [ ] implement search directly into website