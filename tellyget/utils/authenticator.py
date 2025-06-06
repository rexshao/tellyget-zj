from random import randint
from tellyget.utils.cipher import Cipher

import hashlib


class Authenticator:
    def __init__(self, passwd):
        self.cipher = Cipher(passwd.ljust(24, "0")[:24])

    def build(self, token, user_id, stb_id, ip, mac):
        plain_text = '$'.join([str(randint(0, 1e7)).rjust(8, "0"), token, user_id, stb_id, ip, mac, '', 'CTC'])
        return self.cipher.encrypt(plain_text)

    def parse(self, authenticator):
        plain_text = self.cipher.decrypt(authenticator)
        items = plain_text.split('$')
        return {
            'token': items[1],
            'user_id': items[2],
            'stb_id': items[3],
            'ip': items[4],
            'mac': items[5],
        }
