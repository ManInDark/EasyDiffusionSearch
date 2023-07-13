import sqlite3
import os
import asyncio
import sys

if len(sys.argv) < 2:
    IMAGE_ROOT_PATH = "../images"
else:
    IMAGE_ROOT_PATH = sys.argv[1]

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

if ("image",) not in cursor.execute("SELECT name FROM sqlite_master"):
    cursor.execute("CREATE TABLE image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction)")
    print("Created Table, as it did not exist yet")

def insert_image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction):
    cursor.execute("INSERT INTO image VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction))
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
    lora = check_options(content_string, ["LoRA model", "LoRA"])
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

def figure_out_image_path(folder, file, face_correction, upscaling):
    img_path = os.path.join(IMAGE_ROOT_PATH, folder, file)
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
            exit()
    return res[1]

async def parse_txt_file_async(folder, txtfile):
    with open(os.path.join(IMAGE_ROOT_PATH, folder, txtfile), "r") as file:
        lines = file.readlines()
        parsed_content = parse_lines(lines)
        img_path = figure_out_image_path(folder, txtfile.replace(".txt", ".extension"), parsed_content[11], parsed_content[10])

        # insert into database
        if not check_if_image_in_database(img_path):
            insert_image(img_path, *parsed_content)

async def parse_json_file_async(folder, jsonfile):
    import json
    with open(os.path.join(IMAGE_ROOT_PATH, folder, jsonfile), "r") as file:
        content = "".join(file.readlines())
        parsed_content = json.loads(content)
        img_path = figure_out_image_path(folder, jsonfile.replace(".json", ".extension"), parsed_content["use_face_correction"], parsed_content["use_upscale"])

        if not check_if_image_in_database(img_path):
            insert_image(img_path, parsed_content["prompt"], parsed_content["negative_prompt"], parsed_content["seed"], parsed_content["use_stable_diffusion_model"], parsed_content["width"], parsed_content["height"], parsed_content["sampler_name"], parsed_content["num_inference_steps"], parsed_content["guidance_scale"], parsed_content["use_lora_model"], parsed_content["use_upscale"], parsed_content["use_face_correction"])

tasklist = []
async def main():
    for folder in os.listdir(IMAGE_ROOT_PATH):
        for file in os.listdir(os.path.join(IMAGE_ROOT_PATH, folder)):
            if file.endswith(".txt"):
                tasklist.append(asyncio.create_task(parse_txt_file_async(folder, file)))
            elif file.endswith(".json"):
                tasklist.append(asyncio.create_task(parse_json_file_async(folder, file)))
    await asyncio.gather(*tasklist)
    print("Done")
    

if __name__ == "__main__":
    asyncio.run(main())