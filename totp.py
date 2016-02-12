import hmac
import time
from base64 import b64decode
from struct import pack, unpack
from hashlib import sha1


def generateAuthCode(secret):
    counter = int(time.time()) // 30

    secret = b64decode(secret)
    counter = pack('>Q', counter)

    hash = hmac.new(secret, counter, sha1).digest()
    offset = ord(hash[19]) & 0xF

    fullcode = (unpack(">I", hash[offset:offset + 4])[0] & 0x7FFFFFFF)
    chars = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for i in range(5):
        code += chars[fullcode % len(chars)]
        fullcode /= len(chars)

    return code