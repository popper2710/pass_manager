import secrets
import ulid
import os

from .AES import AESCipher


class MasterPassOperator:

    def __init__(self):
        os.makedirs('tmp', exist_ok=True)
        # print(os.getcwd())
        # print(os.listdir('./tmp'))

    def master_pass_recorder(self, password):
        token = secrets.token_bytes(64)

        cipher = AESCipher(key=token)
        e_pass = cipher.encrypt(password)

        file_name = str(ulid.new())

        with open('./tmp/'+file_name, 'wb') as f:
            f.write(e_pass)

        return token.hex()+'$'+file_name

    def master_pass_extractor(self, pass_info):
        token, file_name = pass_info.split('$')

        with open('./tmp/'+file_name, 'rb') as f:
            e_pass = f.read()
        os.remove('./tmp/'+file_name)

        cipher = AESCipher(bytes.fromhex(token))
        password = cipher.decrypt(e_pass).decode()

        new_token = self.master_pass_recorder(password)
        return new_token, password


if __name__ == "__main__":
    Mo = MasterPassOperator()
    session = Mo.master_pass_recorder('test')
    print(session)
    new_token, password = Mo.master_pass_extractor(session)
    print(new_token, password)
    new_token, password = Mo.master_pass_extractor(new_token)
    print(new_token, password)

