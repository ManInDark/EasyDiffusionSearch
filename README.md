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
The query needs to be a SQL WHERE clause in a table with the columns: path, creation_time, prompt, negative_prompt, seed (int), model, width (int), height (int), sampler, steps (int), guidance_scale (float), lora, upscaling, face_correction

Examples:

```
width = 512 AND height = 512
prompt like '%astronaut%'
model like '%sd%'
```