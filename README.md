# EasyDiffuion Image Viewer

This program allows for easily viewing of your generated images.

# How to use

You have to first ingest the data into a database to make it possible to search the images. This is done by executing
```
python ingest.py <path>
```
where \<path\> represents the auto-save location in the webui.

Now you can search for images like this:

```
python search.py "<query>"
```

This then generates a resultsite.html file that can then be opened with the webbrowser of your choice.
The \<query\> is an SQL WHERE clause in a table with the columns: path, prompt, negative_prompt, seed (int), model, width (int), height (int), sampler, steps (int), guidance_scale (float), lora, upscaling, face_correction

Examples:

```
"width = 512 AND height = 512"
"prompt like '%astronaut%'"
"model like '%sd%'"
```

# Moving

In case you want to move the installation you'll have to re-ingest the data.

# Roadmap

- [X] ingest json format too
- [X] check if file already ingested
- [ ] implement search directly into website