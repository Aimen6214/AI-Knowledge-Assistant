import hashlib


def calculate_file_hash(file_bytes: bytes) -> str:
    """
    Returns SHA256 hash of uploaded file.
    """

    sha = hashlib.sha256()
    sha.update(file_bytes)
    return sha.hexdigest()