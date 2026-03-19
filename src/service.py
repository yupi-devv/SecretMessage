import secrets
import string
import uuid
from pathlib import Path
from src.config import stg


UPLOAD_DIR = Path(stg.FILES_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)


def generate_unique_code():
    characters = string.ascii_uppercase + string.digits + string.ascii_lowercase
    code = "".join(secrets.choice(characters) for _ in range(8))
    return code + str(uuid.uuid4()).replace("-", "")
