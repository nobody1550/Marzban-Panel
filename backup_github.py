import os
import base64
import requests
import sqlite3
import tempfile


DB = "/code/db.sqlite3"

TOKEN = os.environ["GITHUB_TOKEN"]
REPO = os.environ["GITHUB_REPO"]

FILE_PATH = "marzban-backup.sqlite3"


def sqlite_backup():

    tmp = tempfile.NamedTemporaryFile(delete=False)

    src = sqlite3.connect(DB)
    dst = sqlite3.connect(tmp.name)

    with dst:
        src.backup(dst)

    src.close()
    dst.close()

    return tmp.name


backup = sqlite_backup()


with open(backup, "rb") as f:
    content = base64.b64encode(f.read()).decode()


url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"


headers = {
    "Authorization": f"Bearer {TOKEN}"
}


# گرفتن SHA فایل قبلی
old = requests.get(url, headers=headers)


data = {
    "message": "automatic marzban backup",
    "content": content
}


if old.status_code == 200:
    data["sha"] = old.json()["sha"]


r = requests.put(
    url,
    headers=headers,
    json=data
)


print(r.status_code)
print(r.text)
