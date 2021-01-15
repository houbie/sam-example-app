import base64
import zlib


def compress_base64(data: str) -> str:
    return base64.b64encode(zlib.compress(data.encode())).decode()


def decompress_base64(encoded_data: str) -> str:
    return zlib.decompress(base64.b64decode(encoded_data)).decode()
