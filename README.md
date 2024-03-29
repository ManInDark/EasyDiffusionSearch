# EasyDiffuion Image Viewer

This program allows for the easy viewing and filtering of images generated with [EasyDiffusion](https://github.com/easydiffusion/easydiffusion).

# How to use

First change the config.json file by setting the image-path to the absolute path of your image folder. This path can simply be copied from the Web UI.

Afterwards you have to ingest the data into a database to make it possible to search the images. This is done by executing
```
python ingest.py
```
This might take a while, but not that long.

Now you can start the search site with
```
python server.py
```
Which can then be opened on localhost:8000

You can now type in a query into the text field at the top of the page and with the press of return it will show you the filtered images.
The query needs to be a SQL WHERE clause in a table with the columns: path, creation_time (datetime, YYYY-MM-DD for filter), prompt, negative_prompt, seed (int), model, width (int), height (int), sampler, steps (int), guidance_scale (float), lora, upscaling, face_correction

Examples: (Standard Search)

```
1 order by creation_time desc
width = 512 AND height = 512
creation_time > '2024-01-01'
prompt like '%astronaut%'
model like '%sd%'
```

Examples: (Simple Search)

```

512x512
astronaut
sd
```
