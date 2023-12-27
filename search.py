import os
if not os.path.isfile("config.json"):
    print("config.json not found, please create one")
    exit()

import json
with open("config.json", "r") as f:
    IMAGE_ROOT_PATH = json.load(f)["image-path"]

import sqlite3
connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.row_factory = sqlite3.Row

def get_1024x512_images():
    return cursor.execute("SELECT path FROM image WHERE width = '512' AND height = '1024'").fetchall()

def search(query: str, page: int = 0, page_size: int = 30):
    try:
        return cursor.execute(f"SELECT * FROM image WHERE {query} LIMIT {page_size} OFFSET {page * page_size}").fetchall()
    except sqlite3.OperationalError:
        return []

def count(query: str) -> int:
    try:
        return cursor.execute(f"SELECT COUNT(*) FROM image WHERE {query}").fetchone()[0]
    except sqlite3.OperationalError:
        return -1

def read_site() -> str:
    with open("searchsite.html", "r") as f:
        return "".join(f.readlines())

def create_image_string(query: str, local=False, page: int = 0, page_size: int = 30) -> str:
    results = search(query, page, page_size)
    sum_string = ""

    for result in results:
        options = f"Path: {result['path'].replace(IMAGE_ROOT_PATH, '').strip('/')}\nCreation Time: {result['creation_time']}\nPrompt: {result['prompt']}\nNegative Prompt: {result['negative_prompt']}\nSeed: {result['seed']}\nModel: {result['model']}\nSize: {result['width']}x{result['height']}\nSampler: {result['sampler']}\nSteps: {result['steps']}\nGuidance Scale: {result['guidance_scale']}\nLoRA: {result['lora']}\nUpscaling: {result['upscaling']}\nFace Correction: {result['face_correction']}\n"
        sum_string += f"<img src='{result[0].replace(IMAGE_ROOT_PATH, '').strip('/') if local else result[0]}' title='{options}'>\n"
    return sum_string

def search_to_html(query: str):
    site = read_site().replace("<br>", create_image_string(query))
    with open("resultsite.html", "w") as f:
        f.write(site)

import sys
if __name__ == "__main__" and len(sys.argv) > 1:
    search_to_html(sys.argv[1])
