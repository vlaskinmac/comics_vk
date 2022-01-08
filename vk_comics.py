import logging
import os
import random

import requests

from dotenv import load_dotenv


def get_image_comics():
    number_comics = random.randint(1, 2560)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    collection_images = response.json()
    image_comics = requests.get(collection_images["img"])
    image_comics.raise_for_status()
    with open("comics.png", "wb") as file:
        file.write(image_comics.content)
    return response


def get_params_for_save_photo():
    response = get_image_comics()
    collection_photo = response.json()
    title = collection_photo["alt"]
    payload = {"access_token": vk_token, "v": VERSION_VK}
    with open("comics.png", "rb") as file:
        files = {
            "photo": file,
        }
        os.remove("./comics.png")
        url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
        get_url_for_upload = requests.get(url_for_upload, params=payload)
        get_url_for_upload.raise_for_status()
        get_url_save_photo = get_url_for_upload.json()["response"]["upload_url"]
        params_for_save_photo = requests.post(get_url_save_photo, files=files, params=payload)
        params_for_save_photo.raise_for_status()
        return params_for_save_photo.json(), title


def saves_photo():
    params_for_save_photo, _ = get_params_for_save_photo()
    payload_save_image = {
        "access_token": vk_token, "v": VERSION_VK,
        "hash": params_for_save_photo["hash"],
        "photo": params_for_save_photo["photo"],
        "server": params_for_save_photo["server"],
    }
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    url_photos = requests.post(url_save_photo, params=payload_save_image)
    url_photos.raise_for_status()
    return url_photos.json()


def get_id_numbers():
    url_photos = saves_photo()
    _, title = get_params_for_save_photo()
    id_numbers = [(id_number["id"], id_number["owner_id"]) for id_number in url_photos["response"]]
    for unpacking_id_number in id_numbers:
        photo_id, owner_id = unpacking_id_number
        signed = 1
        payload_wall = {
            "access_token": vk_token, "v": VERSION_VK,
            "filter": "suggests, postponed",
            "from_group": signed,
            "owner_id": group_id,
            "attachments": f"photo{owner_id}_{photo_id}",
            "message": title,
        }

        url_wall_get = f"https://api.vk.com/method/wall.post"
        response_wall_post = requests.post(url_wall_get, params=payload_wall)
        response_wall_post.raise_for_status()



if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    group_id = os.getenv("GROUP_ID")
    VERSION_VK = 5.131
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )
    get_id_numbers()
