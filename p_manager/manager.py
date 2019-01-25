import hashlib
import pickle
import secrets
import string
import sys

import ulid
import MySQLdb
import lepl.apps.rfc3696

from .AES import AESCipher


def check_master_pass(mail, master_pass):
    with open('p_manager/.pass_hash', 'rb') as f:
        hash_pkl = pickle.load(f)
        check_hash = hash_pkl['hash']
        num = hash_pkl['num']
        salt = hash_pkl['salt']
    input_hash = hashlib.pbkdf2_hmac('sha256', (master_pass+mail).encode(), salt, num)

    assert check_hash == input_hash, 'Invalid password or email'
    return master_pass


def create_master_pass(mail, password):
    new_salt = secrets.token_bytes(64)
    new_num = secrets.choice(range(100000, 150000))
    email_validator = lepl.apps.rfc3696.Email()

    if not email_validator(mail):
        return False

    new_hash = hashlib.pbkdf2_hmac('sha256', (password+mail).encode(), new_salt, new_num)

    with open('.pass_hash', 'wb') as f:
        hash_dict = {
            'hash': new_hash,
            'num': new_num,
            'salt': new_salt
        }
        pickle.dump(hash_dict, f)


class DBOperation:
    def __init__(self, master_pass):
        self.conn = MySQLdb.connect(db='pass_db', user='pw_manager', passwd=master_pass)
        self.c = self.conn.cursor()
        self.master_pass = master_pass

        try:
            self.c.execute('SELECT 1 FROM pass_table limit 1;')
            # self.c.execute('DROP TABLE pass_table;')
        except MySQLdb.Error:
            self.c.execute('''
            CREATE TABLE pass_table(
            pass_id CHAR(26) NOT NULL PRIMARY KEY ,
            password BLOB,
            purpose TEXT,
            description TEXT
            )
            ''')
            print("Create new table because can't find it.")

    def __del__(self):
        self.c.close()
        self.conn.close()

    def insert_pass_row(self, password, purpose='No text', description='No text'):
        c = self.c
        conn = self.conn
        pass_id = ulid.new()
        e_pass = self.encrypt_pass(password)

        sql = 'INSERT INTO pass_table VALUES(%s, %s, %s, %s)'
        c.execute(sql, (pass_id, e_pass, purpose, description))

        conn.commit()
        print('Insert Success')

    def update_pass_row(self, pass_id, new_row):
        c = self.c
        conn = self.conn
        for k, v in new_row.items:
            sql = 'UPDATE pass_TABLE SET %s = %s WHERE ID = %s'
            c.execute(sql, (k, v, pass_id))
        conn.commit()
        print('Update Success')
        return None

    def show_table(self):
        c = self.c
        c.execute('SELECT pass_id, purpose, description FROM pass_table')
        result = c.fetchall()
        for row in result:
            print('|',end='')
            for i in row:
                print(i + ' |', end='')
            print('')

        return None

    def select_row(self, pass_id):
        c = self.c
        sql = 'SELECT * FROM pass_table WHERE pass_id = %s'
        c.execute(sql, (pass_id,))
        result = c.fetchall()
        return result

    def create_key(self):
        c = self.c
        conn = self.conn
        try:
            c.execute('SELECT 1 FROM key_table limit 1;')
            # c.execute('DROP TABLE key_table;')
        except MySQLdb.Error:
            c.execute('''
            CREATE TABLE key_table(
            key_id TINYINT UNSIGNED AUTO_INCREMENT,
            salt BINARY(128),
            num INT(7),
            INDEX(key_id)
            )
            ''')
            print("Create new key_table because can't find table.", file=sys.stderr)

        salt = secrets.token_bytes(128)
        num = secrets.choice(range(1000000, 1500000))
        sql = 'INSERT INTO key_table(salt, num) VALUES (%s, %s)'
        c.execute(sql, (salt, num))
        conn.commit()
        print('Success to create new key!!')
        return None

    def extract_key(self, key_id):
        master_pass = self.master_pass
        c = self.c
        sql = 'SELECT * FROM key_table WHERE key_id = %s'
        c.execute(sql, (key_id,))
        k_result = c.fetchall()[0]
        key = hashlib.pbkdf2_hmac('sha256', master_pass.encode(), k_result[1], k_result[2])
        return key

    def encrypt_pass(self, password):
        c = self.c
        self.create_key()
        c.execute('SELECT key_id FROM key_table')
        id_ls = c.fetchall()[0]
        select_id = secrets.choice(id_ls)
        key = self.extract_key(select_id)

        cipher = AESCipher(key=key)
        e_pass = cipher.encrypt(password)
        str_id = str(select_id)
        len_id = 3 - len(str_id)
        if len_id > 0:
            str_id = '0'*len_id + str_id
        return e_pass.decode() + str_id

    def decrypt_pass(self, e_pass):
        key_id = int(e_pass[-3:])
        key = self.extract_key(key_id)
        cipher = AESCipher(key)
        password = cipher.decrypt(e_pass[:-3])

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
    mail = 'hige1332@yahoo.co.jp'
    password = 'test'
    # create_master_pass(mail,password)
    check_master_pass(mail, password)
