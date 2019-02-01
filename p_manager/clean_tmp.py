import os
import ulid
import datetime


def clean_tmp():
    if not os.path.exists('./tmp'):
        return None

    file_list = os.listdir('./tmp')
    # print(file_list)
    # os.chdir('./tmp')

    for file_name in file_list:
        check_time = ulid.from_str(file_name).timestamp().datetime + datetime.timedelta(hours=9, minutes=15)
        now = datetime.datetime.now()
        if now >= check_time:
            os.remove(file_name)
            print('remove tmp_file:{}'.format(file_name))


if __name__ == "__main__":
    clean_tmp()
