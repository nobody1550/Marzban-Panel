import os
import sqlite3
import tempfile
from datetime import datetime

import boto3


DB_PATH = "/code/db.sqlite3"

r2 = boto3.client(
    "s3",
    endpoint_url=os.environ["R2_ENDPOINT"],
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
)


bucket = os.environ["R2_BUCKET"]


def create_backup():

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".sqlite3",
        delete=False
    )

    temp_file.close()

    source = sqlite3.connect(DB_PATH)
    destination = sqlite3.connect(temp_file.name)

    with destination:
        source.backup(destination)

    source.close()
    destination.close()

    return temp_file.name


backup_file = create_backup()

filename = (
    "marzban-"
    + datetime.now().strftime("%Y-%m-%d-%H-%M")
    + ".sqlite3"
)


r2.upload_file(
    backup_file,
    bucket,
    filename
)


os.remove(backup_file)

print("Backup uploaded:", filename)
