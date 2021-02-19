# from .hash2way import encode_data, decode_data, gen_ciph
# from django.conf import settings as st
import secrets

# START = settings.AUTH_START
# STEP = settings.AUTH_STEP

# def encode(cipher, data):
#     return encode_data(data, cipher)

# def decode(cipher, data):
#     return encode_data(data, cipher)

# def get_cipher(block_size=32):
#     return gen_ciph(block_size)

def decode_cipher(cipher):
    ciph_list = [cipher[0:9], cipher[9:17], cipher[17:25], cipher[25:]]
    random_ciph = ""
    for x in ciph_list:
        random_ciph += randomize(x)
    return random_ciph

def randomize(part):
    index = range(0,len(part), 2)
    list_part = [part[x] for x in index]
    return "".join(list_part)


def get_api_key():
    return secrets.token_urlsafe(32)
