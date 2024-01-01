import os
if not os.path.isfile("config.json"):
    print("config.json not found, please create one")
    exit()

import datetime
import time
DATE_FORMAT = "%Y-%m-%d"
def convert_date_string_to_unix(s: str):
    date = datetime.datetime.strptime(s, DATE_FORMAT)
    date = datetime.datetime(date.year, date.month, date.day, tzinfo=datetime.timezone.utc) # Extra reconverting required https://github.com/python/cpython/issues/94757
    return date.timestamp()

LAST_SCANNED_FOLDER_DATE_DEFAULT_CONFIG_VALUE = datetime.datetime(1970, 1, 1).strftime(DATE_FORMAT)
LAST_SCANNED_FOLDER_DATE_DEFAULT = convert_date_string_to_unix(LAST_SCANNED_FOLDER_DATE_DEFAULT_CONFIG_VALUE)
ONE_DAY = 60 * 60 * 24

import json
with open("config.json", "r") as f:
    data = json.load(f)
    IMAGE_ROOT_PATH = data["image-path"]
    if IMAGE_ROOT_PATH == "":
        print("Please set \"image-path\" in config.json")
        exit()

    if "last-scanned-folder-date" not in data:
        data["last-scanned-folder-date"] = LAST_SCANNED_FOLDER_DATE_DEFAULT_CONFIG_VALUE

    try:
        LAST_SCANNED_FOLDER_DATE = convert_date_string_to_unix(data["last-scanned-folder-date"])
    except:
        print("Failed to read \"last-scanned-folder-date\" from config.json, make sure it's a string in YYYY-MM-DD format, for example 2023-12-31")
        exit()

def update_config():
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)

import sqlite3
connection = sqlite3.connect("database.db")
cursor = connection.cursor()

import asyncio

if ("image",) not in cursor.execute("SELECT name FROM sqlite_master"):
    cursor.execute("CREATE TABLE image(path, creation_time, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction)")
    LAST_SCANNED_FOLDER_DATE = LAST_SCANNED_FOLDER_DATE_DEFAULT # Force ingest
    print("Created Table, as it did not exist yet")

def insert_image(path, creation_time, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction):
    if isinstance(lora, list):
        lora = " ".join(lora)
    cursor.execute("INSERT INTO image VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (path, creation_time, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction))
    connection.commit()

def check_if_image_in_database(path):
    return len(list(cursor.execute("SELECT path FROM image WHERE path=?", (path,)))) > 0

def get_value_for(content_string: str, name: str) -> str:
    index = content_string.index(name)
    ind_str = content_string[index + len(name):]
    return ind_str[:ind_str.index("\n")].strip() 

def check_options(content_string, name_options):
    for option in name_options:
        if option in content_string:
            return get_value_for(content_string, option)
    return "???"

def parse_lines(content):
    content_string = "".join(content) + "\n"

    prompt = content[0].replace("Prompt: ", "").strip()
    negative_prompt = get_value_for(content_string, "Negative Prompt: ")
    seed = int(get_value_for(content_string, "Seed: "))
    model = check_options(content_string, ["Stable Diffusion model", "Stable Diffusion Model"])
    width = int(get_value_for(content_string, "Width: "))
    height = int(get_value_for(content_string, "Height: "))
    sampler = get_value_for(content_string, "Sampler: ")
    steps = int(get_value_for(content_string, "Steps: "))
    guidance_scale = float(get_value_for(content_string, "Guidance Scale: "))
    lora = check_options(content_string, ["LoRA model: ", "LoRA: "])
    upscaling = get_value_for(content_string, "Use Upscaling: ")
    face_correction = get_value_for(content_string, "Use Face Correction: ")

    return (prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction)

def test_extensions(path: str) -> tuple[bool, str]:
    if os.path.isfile(path.replace(".extension", ".jpeg")):
        return (True, path.replace(".extension", ".jpeg"))
    elif os.path.isfile(path.replace(".extension", ".png")):
        return (True, path.replace(".extension", ".png"))
    else:
        return (False, path)

def figure_out_image_path(file, face_correction, upscaling):
    """
    Returns the path to the image. Will return None if image path not valid
    """

    img_path = file
    res = test_extensions(img_path)
    if not res[0]:
        if not face_correction == "None": # face correction
            img_path = img_path.replace(".extension", f"_{face_correction}.extension")
        if not upscaling == "None": # upscaling
            img_path = img_path.replace(".extension", f"_{upscaling}.extension")
        res = test_extensions(img_path)
        if not res[0]:
            print("Could not find file")
            print(face_correction, upscaling, img_path)
            return None
    return res[1]

async def parse_txt_file_async(txtfile_path: str, txtfile_time: str):
    with open(txtfile_path, "r") as file:
        lines = file.readlines()
        # This needs much better validation for detecting if it's a true metadata file, aswell as optional keys like use_lora_model
        if lines.__len__() <= 0:
            return

        parsed_content = parse_lines(lines)
        img_path = figure_out_image_path(txtfile_path.replace(".txt", ".extension"), parsed_content[11], parsed_content[10])

        if img_path is not None and not check_if_image_in_database(img_path):
            insert_image(img_path, txtfile_time, *parsed_content)

async def parse_json_file_async(jsonfile_path: str, jsonfile_time: str):
    import json
    with open(jsonfile_path, "r") as file:
        lines = file.readlines()
        # This needs much better validation for detecting if it's a true metadata file
        if lines.__len__() <= 0:
            return

        content = "".join(lines)
        parsed_content = json.loads(content)
        if "use_lora_model" not in parsed_content:
            parsed_content["use_lora_model"] = []
            #parsed_content["lora_alpha"] = []

        img_path = figure_out_image_path(jsonfile_path.replace(".json", ".extension"), parsed_content["use_face_correction"], parsed_content["use_upscale"])

        if img_path is not None and not check_if_image_in_database(img_path):
            insert_image(img_path, jsonfile_time, parsed_content["prompt"], parsed_content["negative_prompt"], parsed_content["seed"], parsed_content["use_stable_diffusion_model"], parsed_content["width"], parsed_content["height"], parsed_content["sampler_name"], parsed_content["num_inference_steps"], parsed_content["guidance_scale"], parsed_content["use_lora_model"], parsed_content["use_upscale"], parsed_content["use_face_correction"])

async def main():
    tasklist = []
    last_date = 0
    
    scanned_day = datetime.datetime.fromtimestamp(LAST_SCANNED_FOLDER_DATE).strftime(DATE_FORMAT)
    print(f"Scanning all directories created on the same day and after {scanned_day}. (This can be changed in config.json with \"last-scanned-folder-date\", YYYY-MM-DD format)")

    for root, directories, file_names in os.walk(IMAGE_ROOT_PATH):
        for file_name in file_names:
            file_path = os.path.join(root, file_name)
            file_time = os.path.getctime(file_path)
            file_date = (file_time // ONE_DAY) * ONE_DAY # Truncate to day

            # Allow re-scanning files on the same day they are created
            if file_date < LAST_SCANNED_FOLDER_DATE:
                continue

            if last_date <= file_date:
                last_date = file_date

            if file_name.endswith(".txt"):
                tasklist.append(asyncio.create_task(parse_txt_file_async(file_path, file_time)))
            elif file_name.endswith(".json"):
                tasklist.append(asyncio.create_task(parse_json_file_async(file_path, file_time)))
    await asyncio.gather(*tasklist)
    # Only update if new files were actually added
    if tasklist.__len__() > 0:
        next_date = datetime.datetime.fromtimestamp(last_date).strftime(DATE_FORMAT)
        data["last-scanned-folder-date"] = next_date
        update_config()
        print(f"Next scan date set to {next_date}")
    print("Done")
    

if __name__ == "__main__":
    asyncio.run(main())
