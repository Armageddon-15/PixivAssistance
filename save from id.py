from typing import Union
from Parameters import *
from Illust import api

import Illust
import os


Illust.api = Illust.login()


def save_from_id(id: int, index: Union[list, int] = 0):
    data_file_path = illust_data_path + str(id) + data_extension
    is_exist = os.path.exists(data_file_path)
    if type(index) is list:
        print("length of list is %d" % len(index))
    elif index > 0:
        print("1 picture")
    else:
        print("all pictures")
    illust = Illust.Illust(Illust.api.illust_detail(id).illust)
    illust.saveAll(index)

    if not is_exist:
        illust.deleteCache()


id = 101021358
# index = list(range(1, 4))
index = 1
# int or list

save_from_id(id, index)
