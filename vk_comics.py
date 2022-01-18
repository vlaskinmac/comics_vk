import logging
import os
import random
from pprint import pprint

import requests

from dotenv import load_dotenv


def get_image_comics_content():
    number_comics = random.randint(1, 2560)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    image_comics_content = requests.get(url)
    image_comics_content.raise_for_status()
    # pprint(image_comics_content.json())
    return image_comics_content.json()


def get_image_title_comics():
    collection_images = get_image_comics_content()
    # pprint(collection_images)
    image_comics = requests.get(collection_images["img"])
    title_comics = collection_images["alt"]
    image_comics.raise_for_status()
    with open("comics.png", "wb") as file:
        file.write(image_comics.content)
    return title_comics


def get_content_for_save_photo():
    title = get_image_title_comics()
    # files = get_files_photos()
    payload = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "group_id": group_id,
        }
    url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
    # print(url_for_upload)
    get_url_for_upload = requests.get(url_for_upload, params=payload)
    get_url_for_upload.raise_for_status()
    get_url_save_photo = get_url_for_upload.json()["response"]["upload_url"]
    # pprint(get_url_for_upload.json())
    with open("comics.png", "rb") as file:
        try:
            files = {
                "photo": file,
            }
            params_for_save_photo = requests.post(get_url_save_photo, files=files, params=payload)
        finally:
            os.remove("./comics.png")
    # pprint(params_for_save_photo.json())
    params_for_save_photo.raise_for_status()
    return params_for_save_photo.json(), title


def get_content_url_photos():
    params_for_save_photo, _ = get_content_for_save_photo()
    # pprint(params_for_save_photo)
    payload_save_image = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "hash": params_for_save_photo["hash"],
        "photo": params_for_save_photo["photo"],
        "server": params_for_save_photo["server"],
    }
    # pprint(payload_save_image)
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    url_photos = requests.post(url_save_photo, params=payload_save_image)
    url_photos.raise_for_status()

    pprint(url_photos.json())
    return url_photos.json()


def posts_comics():
    url_photos = get_content_url_photos()
    # pprint(url_photos)

    _, title = get_content_for_save_photo()

    # id_numbers = [(id_number["id"], id_number["owner_id"]) for id_number in url_photos["response"]]
    # for unpacking_id_number in id_numbers:
    #     photo_id, owner_id = unpacking_id_number
    signed = 1
    payload_wall = {
        "access_token": vk_token, "v": VERSION_VK,
        "filter": "suggests, postponed",
        "from_group": signed,
        "owner_id": group_id,
        "attachments": f"photo{user_id}_{int(*[i['id'] for i in url_photos['response']])}",
        "message": title,
    }
    url_wall_get = f"https://api.vk.com/method/wall.post"
    response_wall_post = requests.post(url_wall_get, params=payload_wall)
    response_wall_post.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    group_id = os.getenv("GROUP_ID")
    user_id = os.getenv("user_id")
    VERSION_VK = 5.131
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )
    posts_comics()
