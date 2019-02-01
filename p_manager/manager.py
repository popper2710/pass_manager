import hashlib
import pickle
import secrets
import string

import base64
import MySQLdb

from .AES import AESCipher


def create_master_pass(username, password):
    with open('.db_info', 'wb') as f:
        hash_dict = {
            'username': username,
            'password': password,
        }
        pickle.dump(hash_dict, f)


class DBOperation:
    def __init__(self, crypt_pass):
        with open('.db_info', 'rb') as f:
            db_info = pickle.load(f)

        self.conn = MySQLdb.connect(db='pass_db', user=db_info['username'], passwd=db_info['password'])
        self.c = self.conn.cursor()
        self.crypt_pass = crypt_pass

    def __del__(self):
        self.c.close()
        self.conn.close()

    def encrypt_pass(self, password):
        crypt_pass = self.crypt_pass
        salt = secrets.token_bytes(64)
        num = secrets.choice(range(2500000, 3000000))
        key = hashlib.pbkdf2_hmac('sha256', crypt_pass.encode(), salt, num)

        cipher = AESCipher(key=key)
        s_num = str(num)
        s_salt = base64.b64encode(salt).decode('ascii')
        e_pass = '$'.join([s_num, s_salt, cipher.encrypt(password).decode('ascii')])

        return e_pass

    def decrypt_pass(self, e_pass):
        pass_list = e_pass.split('$')
        crypt_pass = self.crypt_pass

        num = int(pass_list[0])
        salt = base64.b64decode(pass_list[1].encode('ascii'))
        key = hashlib.pbkdf2_hmac('sha256', crypt_pass.encode(), salt, num)

        cipher = AESCipher(key)
        password = cipher.decrypt(pass_list[2].encode('ascii'))

        return password.decode()


def create_pass(pass_len=16, uppercase=True, symbol=True):
    if pass_len <= 4:
        print('Password is Too short!!')
        return None
    elif pass_len >= 101:
        print('Password is Too long!!')
        return None

    if uppercase:
        pass_index = string.ascii_letters + string.digits
    else:
        pass_index = string.ascii_lowercase + string.digits

    if symbol:
        pass_index += string.punctuation

    while True:
        password = "".join([secrets.choice(pass_index) for i in range(pass_len)])
        if all([
            any(c.isdigit for c in password),
            any(c.isalpha for c in password),
        ]):
            if any(c in string.punctuation for c in password) or not symbol:
                return password


if __name__ == '__main__':
    operation = DBOperation('test')
    e_pass = operation.encrypt_pass('-'*100)
    print(e_pass)
    print(operation.decrypt_pass(e_pass))

