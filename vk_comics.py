import logging
import os
import random

import requests

from dotenv import load_dotenv
from requests import HTTPError


def check_for_response(response):
    if HTTPError().response:
        raise HTTPError(f'{response} - {HTTPError.__name__}')


def get_end_page():
    url = f"https://xkcd.com/info.0.json"
    try:
        image_comics_content = requests.get(url)
        image_comics_content.raise_for_status()
        check_for_response(image_comics_content)
        return image_comics_content.json()["num"]
    except HTTPError as exc:
        logging.warning(exc)


def get_image_title_content(end_page):
    number_comics = random.randint(1, end_page)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    try:
        image_content = requests.get(url)
        image_content.raise_for_status()
        check_for_response(image_content)
    except HTTPError as exc:
        logging.warning(exc)
    image_link = image_content.json()["img"]
    title = image_content.json()["alt"]
    try:
        image_comics = requests.get(image_link)
        image_comics.raise_for_status()
        check_for_response(image_comics)
        return image_comics, title
    except HTTPError as exc:
        logging.warning(exc)


def save_image_file_comics(image_comics):
    with open("comics.png", "wb") as file:
        file.write(image_comics.content)


def get_content_for_save_photo():
    payload = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "group_id": group_id,
    }
    url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
    try:
        url_for_upload = requests.get(url_for_upload, params=payload)
        check_for_response(url_for_upload)
        url_for_upload.raise_for_status()
        get_url_save_photo = url_for_upload.json()["response"]["upload_url"]
    except HTTPError as exc:
        logging.warning(exc)

    with open("comics.png", "rb") as file:
        try:
            files = {
                "photo": file,
            }
            params_for_save_photo = requests.post(get_url_save_photo, files=files, params=payload)
            check_for_response(params_for_save_photo)
            params_for_save_photo.raise_for_status()
            return params_for_save_photo.json()
        except HTTPError as exc:
            logging.warning(exc)
        finally:
            os.remove("./comics.png")


def get_content_url_photos(hash, photo, server):
    payload_save_image = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "hash": hash,
        "photo": photo,
        "server": server,
        "group_id": group_id,
    }
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    try:
        url_photos = requests.post(url_save_photo, params=payload_save_image)
        url_photos.raise_for_status()
        check_for_response(url_photos)
        return url_photos.json()
    except HTTPError as exc:
        logging.warning(exc)


def posts_comics(media_id, title):
    signed = 1
    payload_wall = {
        "access_token": vk_token, "v": VERSION_VK,
        "filter": "suggests, postponed",
        "from_group": signed,
        "owner_id": f"-{group_id}",
        "attachments": f"photo{user_id}_{media_id}",
        "message": title,
    }
    url_wall_get = f"https://api.vk.com/method/wall.post"
    try:
        requests.post(url_wall_get, params=payload_wall)
        requests.raise_for_status()
        check_for_response(requests)
    except HTTPError as exc:
        logging.warning(exc)


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

    end_page = get_end_page()
    image_comics, title = get_image_title_content(end_page)
    save_image_file_comics(image_comics)
    params_for_save_photo = get_content_for_save_photo()
    url_photos = get_content_url_photos(
        params_for_save_photo["hash"],
        params_for_save_photo["photo"],
        params_for_save_photo["server"]
    )
    posts_comics(url_photos['response'][0]['id'], title)
