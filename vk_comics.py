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


def get_comics_end_page():
    url = f"https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    response_content = response.json()
    return response_content["num"]


def get_image_title_content(end_page_comics, img_name):
    number_comics = random.randint(1, end_page_comics)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()
    image_link = comics["img"]
    title = comics["alt"]
    image_comics = requests.get(image_link)
    image_comics.raise_for_status()

    with open(img_name, "wb") as file:
        file.write(image_comics.content)
    return title


def get_params_for_save_photo(vk_token, version_vk, group_id, img_name):
    payload = {
        "access_token": vk_token,
        "v": version_vk,
        "group_id": group_id,
    }
    url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
    response = requests.get(url_for_upload, params=payload)
    response.raise_for_status()
    response_content = response.json()
    check_for_response(response_content)
    upload_url = response_content["response"]["upload_url"]
    with open(img_name, "rb") as file:
        files = {
            "photo": file,
        }
        params_for_save_photo = requests.post(upload_url, files=files, params=payload)
    params_for_save_photo.raise_for_status()
    response_content = params_for_save_photo.json()
    check_for_response(response_content)
    return response_content


def save_photo(hash_code, photo, server, vk_token, version_vk, group_id):
    payload_save_image = {
        "access_token": vk_token,
        "v": version_vk,
        "hash_code": hash_code,
        "photo": photo,
        "server": server,
        "group_id": group_id,
    }
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    response = requests.post(url_save_photo, params=payload_save_image)
    response_content = response.json()
    response.raise_for_status()
    check_for_response(response_content)
    return response_content


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
    response_payload_wall = requests.post(url_wall_get, params=payload_wall)
    response_payload_wall.raise_for_status()
    response_content = response_payload_wall.json()
    check_for_response(response_content)


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
    img_name = "comics.png"
    try:
        end_page_comics = get_comics_end_page()
        title = get_image_title_content(end_page_comics, img_name)
        params_for_save_photo = get_params_for_save_photo(vk_token, version_vk, group_id, img_name)
        url_photos = save_photo(
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
    finally:
        os.remove(img_name)



