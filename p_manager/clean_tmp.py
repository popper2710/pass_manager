import os
import ulid
import datetime


def clean_tmp():
    if not os.path.exists('./tmp'):
        return None

    file_list = os.listdir('./tmp')
    os.chdir('./tmp')

    for file_name in file_list:
        make_time = ulid.from_str(file_name).timestamp().datetime
        now = datetime.datetime.now()
        if now > make_time + datetime.timedelta(minutes=15):
            os.remove(file_name)


if __name__ == "__main__":
    clean_tmp()