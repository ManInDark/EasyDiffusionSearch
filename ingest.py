import sqlite3
import os
import asyncio

IMAGE_ROOT_PATH = "../images"

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

if ("image",) not in cursor.execute("SELECT name FROM sqlite_master"):
    cursor.execute("CREATE TABLE image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction)")
    print("Created Table, as it did not exist yet")

def insert_image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction):
    cursor.execute("INSERT INTO image VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora, upscaling, face_correction))
    connection.commit()

def get_value_for(content_string: str, name: str) -> str:
    index = content_string.index(name)
    return content_string[index + len(name):content_string[index:].index("\n") + index].strip() 

def get_model_main(content_string: str) -> str:
    if "Stable Diffusion model" in content_string:
        return get_value_for(content_string, "Stable Diffusion model: ")
    elif "Stable Diffusion Model" in content_string:
        return get_value_for(content_string, "Stable Diffusion Model: ")
    else:
        return "???"

def get_model_LoRA(content_string: str) -> str:
    if "LoRA model" in content_string:
        return get_value_for(content_string, "LoRA model: ")
    elif "LoRA" in content_string:
        return get_value_for(content_string, "LoRA: ")
    else:
        return "???"

def parse_lines(content):
    content_string = "".join(content) + "\n"

    prompt = content[0].replace("Prompt: ", "").strip()
    negative_prompt = get_value_for(content_string, "Negative Prompt: ")
    seed = get_value_for(content_string, "Seed: ")
    model = get_model_main(content_string)
    width = get_value_for(content_string, "Width: ")
    height = get_value_for(content_string, "Height: ")
    sampler = get_value_for(content_string, "Sampler: ")
    steps = get_value_for(content_string, "Steps: ")
    guidance_scale = get_value_for(content_string, "Guidance Scale: ")
    lora = get_model_LoRA(content_string)
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

async def parse_file_async(folder, txtfile):
    with open(os.path.join(IMAGE_ROOT_PATH, folder, txtfile), "r") as file:
        lines = file.readlines()
        try:
            # figure out image path
            parsed_content = parse_lines(lines)
            img_path = os.path.join(IMAGE_ROOT_PATH, folder, txtfile.replace(".txt", ".extension"))
            res = test_extensions(img_path)
            if not res[0]:
                if not parsed_content[11] == "None": # face correction
                    img_path = img_path.replace(".extension", f"_{parsed_content[11]}.extension")
                if not parsed_content[10] == "None": # upscaling
                    img_path = img_path.replace(".extension", f"_{parsed_content[10]}.extension")
            res = test_extensions(img_path)
            if not res[0]: 
                print("Could not find file")
                print(parsed_content, img_path)
                exit()

            # insert into database
            insert_image(img_path, *parsed_content)
        except Exception as e:
            print(lines)
            print(os.path.join(IMAGE_ROOT_PATH, folder, txtfile))
            raise e

tasklist = []
async def main():
    for folder in os.listdir(IMAGE_ROOT_PATH):
        for txtfile in os.listdir(os.path.join(IMAGE_ROOT_PATH, folder)):
            if txtfile.endswith(".txt"):
                tasklist.append(asyncio.create_task(parse_file_async(folder, txtfile)))
    await asyncio.gather(*tasklist)
    print("Done")
    

if __name__ == "__main__":
    asyncio.run(main())