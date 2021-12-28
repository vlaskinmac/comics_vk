import os
from pprint import pprint

import requests
import logging

from dotenv import load_dotenv

load_dotenv()
token=os.getenv("TOKEN")

logging.basicConfig(
        level=logging.WARNING,
        filename="logs.log",
        filemode="w",
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )


def get_json_comics():
    url = "https://xkcd.com/353/info.0.json"
    response = requests.get(url)

    print(response.json()['alt'])

    payload = {"access_token": token, "v": 5.131}
    with open('comics.png', 'rb') as file:
        files = {
            'photo': file,

        }




        url_for_upload = f"https://api.vk.com/method/photos.getWallUploadServer"
        get_url_for_upload = requests.get(url_for_upload, params=payload)
        # pprint(get_url_for_upload.json())


        get_url_save_photo = get_url_for_upload.json()['response']['upload_url']
        params_for_save_photo = requests.post(get_url_save_photo, files=files, params=payload)
        # pprint(params_for_save_photo.json())

        payload_save_image = {"access_token": token, "v": 5.131,
                "hash": params_for_save_photo.json()['hash'],
                "photo": params_for_save_photo.json()['photo'],
                "server": params_for_save_photo.json()['server'],
            }

        # print(params_for_save_photo.json()['photo'])

        url_save_photo = f"https://api.vk.com/method/photos.saveWallPhoto"
        get_url_for_upload = requests.post(url_save_photo, params=payload_save_image)
        # pprint(get_url_for_upload.json())

        payload_wall = {"access_token": token, "v": 5.131,
                              "filter": "suggests, postponed",
                              "from_group": 1,
                              # "group_id": 209816900,
                              # "owner_id": -8037916,
                              "owner_id": -209816900,
                              "attachments": "photo695777185_457239022",
                              "message": f"{response.json()['alt']}",

                              }

        url_wall_get = f"https://api.vk.com/method/wall.post"
        wall_get = requests.post(url_wall_get, params=payload_wall)
        pprint(wall_get.json())



        # url2 = f"https://api.vk.com/method/photos.getUploadServer"


        #

        # pprint(response2.json()['response']['upload_url'])



        #
        #
        #
        # response3 = requests.post(url, params=payload_save_image)



        # response.raise_for_status()
        # logging.warning(response.status_code)



        # pprint(response2.json())
        # print(response.url)
        # return response.json()
get_json_comics()
