import logging
import os
import random

import requests

from dotenv import load_dotenv
from requests import HTTPError


def check_for_response(response):
    if 'error' in response:
        error_message = f"Error {response['error']['error_msg']}"
        raise HTTPError(error_message)


def get_end_page_comics():
    url = f"https://xkcd.com/info.0.json"
    image_comics_content = requests.get(url)
    image_comics_content.raise_for_status()
    return image_comics_content.json()["num"]


def get_image_title_content(end_page_comics):
    number_comics = random.randint(1, end_page_comics)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    comics_content = requests.get(url)
    comics_content.raise_for_status()
    comics = comics_content.json()
    image_link = comics["img"]
    title = comics["alt"]
    image_comics = requests.get(image_link)
    image_comics.raise_for_status()
    with open("comics.png", "wb") as file:
        file.write(image_comics.content)
    return title


def get_params_for_save_photo(vk_token, version_vk, group_id):
    payload = {
        "access_token": vk_token,
        "v": version_vk,
        "group_id": group_id,
    }
    url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
    url_for_upload = requests.get(url_for_upload, params=payload)
    check_for_response(url_for_upload)
    url_for_upload.raise_for_status()
    upload_url = url_for_upload.json()["response"]["upload_url"]
    with open("comics.png", "rb") as file:
        files = {
            "photo": file,
        }
    try:
        params_for_save_photo = requests.post(upload_url, files=files, params=payload)
        check_for_response(params_for_save_photo)
        params_for_save_photo.raise_for_status()
        return params_for_save_photo.json()
    except HTTPError as exc:
        logging.warning(exc)
    finally:
        os.remove("./comics.png")


def saves_photo(hash_code, photo, server, vk_token, version_vk, group_id):
    payload_save_image = {
        "access_token": vk_token,
        "v": version_vk,
        "hash_code": hash_code,
        "photo": photo,
        "server": server,
        "group_id": group_id,
    }
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    url_photos = requests.post(url_save_photo, params=payload_save_image)
    url_photos.raise_for_status()
    check_for_response(url_photos)
    return url_photos.json()


def posts_comics(media_id, title, vk_token, version_vk, group_id):
    signed = 1
    payload_wall = {
        "access_token": vk_token, "v": version_vk,
        "filter": "suggests, postponed",
        "from_group": signed,
        "owner_id": f"-{group_id}",
        "attachments": f"photo{user_id}_{media_id}",
        "message": title,
    }
    url_wall_get = f"https://api.vk.com/method/wall.post"
    requests.post(url_wall_get, params=payload_wall)
    requests.raise_for_status()
    check_for_response(requests)


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    group_id = os.getenv("GROUP_ID")
    user_id = os.getenv("USER_ID")
    version_vk = 5.131
    logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )
    try:
        end_page_comics = get_end_page_comics()
        title = get_image_title_content(end_page_comics)
        params_for_save_photo = get_params_for_save_photo(vk_token, version_vk, group_id)

        url_photos = saves_photo(
            params_for_save_photo["hash_code"],
            params_for_save_photo["photo"],
            params_for_save_photo["server"],
            vk_token,
            version_vk,
            group_id,
        )
        posts_comics(
            url_photos['response'][0]['id'],
            title,
            vk_token,
            version_vk,
            group_id,
        )
    except HTTPError as exc:
        logging.warning(exc)
