import hashlib


def hashed(string: str) -> str:
    return hashlib.md5(string.encode()).hexdigest()[:5]
