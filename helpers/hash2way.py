from Crypto.Cipher import AES
import base64
import os


# # the character used for padding--with a block cipher such as AES, the value
# # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# # used to ensure that your value is always a multiple of BLOCK_SIZE


# one-liner to sufficiently pad the text to be encrypted
def gen_pad(string, block_size, padding):
    return (string + (block_size - len(string) % block_size) * padding).encode('utf-8')

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64


def _encode_aes(cipher, password, block_size, padding):
    return base64.b64encode(cipher.encrypt(gen_pad(password, block_size, padding)))


def _decode_aes(cipher, _encoded, padding):
    return str(cipher.decrypt(base64.b64decode(_encoded)), 'utf-8').rstrip(padding)


# generate a random secret key
# secret = os.urandom(BLOCK_SIZE)
#
# # create a cipher object using the random secret
# c = AES.new(secret, AES.MODE_ECB)
# # encode a string
# encoded = _encode_aes(c, 'password')
# print('Encrypted string:', encoded)
#
# # decode the encoded string
# decoded = _decode_aes(c, encoded)
# print('Decrypted string:', decoded)


def gen_ciph(block_size=32):
    s = os.urandom(block_size)
    return AES.new(s, AES.MODE_ECB)
    

def encode_data(data, cipher, padding='{', block_size=32):
    # generate a random secret key
    

    # create a cipher object using the random secret
    

    encoded_data = _encode_aes(cipher, data, block_size, padding)

    return _encode_aes(cipher, encoded_data, block_size, padding)


def decode_data(data, cipher, padding='{'):
    decoded_data = _decode_aes(cipher, data, padding)
    return _decode_aes(cipher, decoded_data, padding)
