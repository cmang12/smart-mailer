import base64


def encode_key(key):
    return base64.b64encode(key.encode()).decode()
