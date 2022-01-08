# Comics_vk


**Script sends comics to [VK](https://vk.com/) group.**


This script is written as part of the task of the courses [Devman](https://dvmn.org).


<img src="https://user-images.githubusercontent.com/78322994/147877329-8e6127ab-bc69-49ef-8691-6d881ae35f8e.png" alt="drawing" width="650"/>  


## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Python Version

Python 3.6 and later.

### Installing

To install the software, you need to install the dependency packages from the file: **requirements.txt**.

Perform the command:

```

pip3 install -r requirements.txt

```

## Getting API keys

**VK TOKEN**

- Create an application using the link: [`VK TOKEN`](https://dev.vk.com).
- Click "Edit".
- Copy the client_id (id) number from the url.
- Enter in the url - client_id received in the previous step.
- Follow the completed url:

https://oauth.vk.com/authorize?client_id={CLIENT_ID}&display=page&scope=photos,groups&response_type=token&v=5.131&state=123456.

**GROUP ID**

- Get the group_id here: [`GROUP ID`](https://regvk.com/id/)

## Launch code

```python
$ python vk_comics.py
```


## Authors

**vlaskinmac**  - [GitHub-vlaskinmac](https://github.com/vlaskinmac/)


