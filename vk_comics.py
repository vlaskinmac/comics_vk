import logging
import os
import random
import re
from pprint import pprint

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import HTTPError


def get_end_page():
    url = f"https://xkcd.com/"
    response_xkcd = requests.get(url)
    response_xkcd.raise_for_status()
    soup = BeautifulSoup(response_xkcd.text, "lxml")
    line_with_number = soup.select_one("#middleContainer > a")
    end_page = re.search("\d+", str(line_with_number)).group()
    return int(end_page)


def get_image_comics_content(end_page):
    number_comics = random.randint(1, end_page)
    url = f"https://xkcd.com/{number_comics}/info.0.json"
    image_comics_content = requests.get(url)
    image_comics_content.raise_for_status()
    return image_comics_content.json()


def get_image_title_comics(collection_images):
    link_image_comics, title_comics = [content for content in (collection_images["img"], collection_images["alt"])]
    image_comics = requests.get(link_image_comics)
    image_comics.raise_for_status()
    with open("comics.png", "wb") as file:
        file.write(image_comics.content)
    return title_comics


def get_content_for_save_photo():
    payload = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "group_id": group_id,
    }
    url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
    try:
        get_url_for_upload = requests.get(url_for_upload, params=payload)
        pprint(get_url_for_upload.json())
        get_url_save_photo = get_url_for_upload.json()["response"]["upload_url"]
    except HTTPError as exc:
        logging.warning(exc)

    with open("comics.png", "rb") as file:
        try:
            files = {
                "photo": file,
            }
            params_for_save_photo = requests.post(get_url_save_photo, files=files, params=payload)
            params_for_save_photo.raise_for_status()
            return params_for_save_photo.json()
        finally:
            os.remove("./comics.png")


def get_content_url_photos(params_for_save_photo):
    payload_save_image = {
        "access_token": vk_token,
        "v": VERSION_VK,
        "hash": params_for_save_photo["hash"],
        "photo": params_for_save_photo["photo"],
        "server": params_for_save_photo["server"],
        "group_id": group_id,
    }
    url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
    try:
        url_photos = requests.post(url_save_photo, params=payload_save_image)
        return url_photos.json()
    except HTTPError as exc:
        logging.warning(exc)


def posts_comics(url_photos):
    signed = 1
    media_id = url_photos['response'][0]['id']
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
    collection_images = get_image_comics_content(end_page)
    title = get_image_title_comics(collection_images)
    params_for_save_photo = get_content_for_save_photo()
    url_photos = get_content_url_photos(params_for_save_photo)
    posts_comics(url_photos)
