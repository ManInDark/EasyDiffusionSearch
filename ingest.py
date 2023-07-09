import sqlite3
import os
import asyncio
import time

IMAGE_ROOT_PATH = "../images"

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

if ("image",) not in cursor.execute("SELECT name FROM sqlite_master"):
    cursor.execute("CREATE TABLE image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora)")
    print("Created Table, as it did not exist yet")

def insert_image(path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora):
    cursor.execute("INSERT INTO image VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (path, prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora))
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

    return (prompt, negative_prompt, seed, model, width, height, sampler, steps, guidance_scale, lora)

async def parse_file_async(folder, txtfile):
    print(f"Started at {time.strftime('%X')}")
    with open(os.path.join(IMAGE_ROOT_PATH, folder, txtfile), "r") as file:
        lines = file.readlines()
        try:
            parsed_content = parse_lines(lines)
            insert_image(os.path.join(IMAGE_ROOT_PATH, folder, txtfile.replace(".txt", ".png")), *parsed_content)
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