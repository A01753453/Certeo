import hashlib
from typing import BinaryIO

CHUNK_SIZE = 1024 * 1024  # 1 MiB

def sha256_stream(fp: BinaryIO) -> str:
    hasher = hashlib.sha256()
    while True:
        chunk = fp.read(CHUNK_SIZE)
        if not chunk:
            break
        hasher.update(chunk)
    return hasher.hexdigest()
