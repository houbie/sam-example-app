from lambda_lib.util import compress_base64, decompress_base64


def test_compress_decompress():
    data = 1000 * 'hello world'
    compressed = compress_base64(data)
    assert len(compressed) < len(data)
    assert decompress_base64(compressed) == data
