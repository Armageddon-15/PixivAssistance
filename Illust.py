import Parameters
import pixivpy3 as pixiv
import os
import subprocess
import pickle
import time
import random
import requests
import shutil
import datetime
import imageio.v3 as iio
import zipfile
import queue
import threading
import math
import numpy as np
from queue import Queue
from typing import Union
from PAEnum import *
from PAException import *


class Illust:
    def __init__(self, illust):
        self.id = illust.id
        self.title = illust.title
        self.type = illust.type
        self.is_like = illust.is_bookmarked
        self.create_time = None
        self.time_str = ""
        self.block = illust.is_muted

        self.page_count = illust.page_count
        self.tags = []
        self.translate_tags = []
        self.description = illust.caption

        self.user_id = illust.user['id']
        self.user_name = illust.user['name']
        self.user_head = illust.user.profile_image_urls['medium']

        self.sq_preview_url = illust.image_urls['square_medium']
        self.large_urls = []
        self.urls = []
        self.gif_url = ""
        self.gif_delay = []

        self.downloaded = {}
        self.need_thumbnail = True
        self.downloaded_path = ""

        self.checkAI(illust)
        self.getTags(illust)
        self.getCreateTime(illust)
        self.getUrls(illust)

        self.is_nsfw = self.isNSFW()

    def noNeedThumbnail(self):
        self.need_thumbnail = False
        self.saveData()

    def checkAI(self, illust):
        ai_type = illust.illust_ai_type
        if ai_type == 2:
            self.tags.append("AI生成")
            self.translate_tags.append("Pixiv AI label")
        elif ai_type == 1:
            pass
        else:
            print(ai_type)

    def getTags(self, illust):
        for name in illust.tags:
            tag = name['name']
            tltag = self.noneToString(name['translated_name'])
            self.tags.append(tag)
            self.translate_tags.append(tltag)
        # print(self.tags, self.translate_tags)

    def getUrls(self, illust):
        if self.type == "ugoira":
            json_result_gif = api.ugoira_metadata(self.id)
            self.gif_url = json_result_gif.ugoira_metadata.zip_urls.medium
            gif_frame_data = json_result_gif.ugoira_metadata.frames
            print(gif_frame_data)
            for data in gif_frame_data:
                if data.delay < 1:
                    delay = data.delay * 1000
                else:
                    delay = data.delay
                self.gif_delay.append(delay)

        elif self.page_count == 1:
            url = illust.meta_single_page['original_image_url']
            self.urls.append(url)
            large_url = illust.image_urls['large']
            self.large_urls.append(large_url)
        else:
            for num in range(0, self.page_count):
                url = illust.meta_pages[num]['image_urls']['original']
                self.urls.append(url)
                large_url = illust.meta_pages[num]['image_urls']['large']
                self.large_urls.append(large_url)

    def getCreateTime(self, illust):
        s = illust.create_date
        year = int(s[0:4])
        mon = int(s[5:7])
        day = int(s[8:10])
        hour = int(s[11:13])
        minute = int(s[14:16])
        sec = int(s[17:19])
        delta = int(s[20:22])

        t = datetime.datetime(year, mon, day, hour, minute, sec)
        d = datetime.timedelta(hours=delta - Parameters.utc_offset)
        self.create_time = t - d
        self.time_str = "_%d%d%d_%d%d%d" % (year, mon, day, hour, minute, sec)

    def updateIllust(self):
        illust = api.illust_detail(self.id).illust

        self.id = illust.id
        self.title = illust.title
        self.type = illust.type
        self.is_like = illust.is_bookmarked
        self.create_time = None
        self.time_str = ""
        self.block = illust.is_muted

        self.page_count = illust.page_count
        self.tags = []
        self.translate_tags = []
        self.description = illust.caption

        self.user_id = illust.user['id']
        self.user_name = illust.user['name']
        self.user_head = illust.user.profile_image_urls['medium']

        self.sq_preview_url = illust.image_urls['square_medium']
        self.large_urls = []
        self.urls = []
        self.gif_url = ""
        self.gif_delay = []

        self.checkAI(illust)
        self.getTags(illust)
        self.getCreateTime(illust)
        self.getUrls(illust)
        self.is_nsfw = self.isNSFW()
        self.readCustomData()

        self.saveData()

    @property
    def thumbnail_name(self):
        """
        return thumbnail file name
        """
        return str(self.id) + os.path.splitext(self.sq_preview_url)[1]

    @property
    def data_name(self):
        """
        return data file name
        """
        return str(self.id) + Parameters.data_extension

    def getLargeName(self, index=0):
        """
        return cache file name by index
        """
        if self.type == "ugoira":
            return str(self.id) + Parameters.gif_extension
        else:
            return str(self.id) + "_" + str(index) + os.path.splitext(self.large_urls[index])[1]

    def getOriginName(self, index=0):
        """
        return original file name by index and currently only worked in by_index naming method
        """
        return self.setName(index, self.urls[index])

    @property
    def r18_dir(self):
        """
        return empty string if illust sfw
        else return r-18 subfolder path
        """
        if self.is_nsfw:
            r18_path = Parameters.r18_subfolder
        else:
            r18_path = ""
        return r18_path

    @property
    def special_tag_subfolder(self):
        """
        return subfolder of current illust
        empty string if not match any
        """
        subfolder_name = ""
        tag_index_list = []

        for tag in self.tags:
            try:
                subfolder_name = special_tags_dict[tag]
            except KeyError:
                subfolder_name = ""
            else:
                tag_index_list.append(special_tags_sort.index(subfolder_name))

        if len(tag_index_list) > 0:
            tag_index_list.sort()
            subfolder_name = special_tags_sort[tag_index_list[0]]
            subfolder_name += "\\"
            print(subfolder_name)

        return subfolder_name

    def getSavePath(self):
        if self.downloaded_path != "":
            return self.downloaded_path
        else:
            raise FileNotFoundError

    def translateTagsToNone(self):
        for num in range(len(self.translate_tags)):
            self.translate_tags[num] = self.stringToNone(self.translate_tags[num])

    def isDownloadedBefore(self, index):
        if Parameters.check_downloaded:
            try:
                self.downloaded[index]
            except KeyError:
                return False
            else:
                if self.downloaded[index] == DownloadState.successful:
                    return True
                else:
                    return False
        else:
            return False

    def isNSFW(self):
        for tag in self.tags:
            if tag == "R-18" or tag == "R-18G":
                return True
        return False

    @staticmethod
    def noneToString(va):
        if va is not None:
            return va
        else:
            return "!@#empty#@!"

    @staticmethod
    def stringToNone(va):
        if va == "!@#empty#@!":
            return None
        else:
            return va

    @staticmethod
    def checkExisted(dest):
        return os.path.exists(dest)

    def saveThumbnail(self):
        if self.need_thumbnail:
            self.__tryToDownloadFile(self.sq_preview_url, Parameters.illust_thbnl_path + self.thumbnail_name)

    def saveLargeByIndex(self, index):
        """
        save single large pic
        """
        save_path = Parameters.illust_cache_path + self.getLargeName(index)

        if self.type == "ugoira":
            self.downloadGif()
            return save_path, DownloadState.successful
        else:
            result = self.__tryToDownloadFile(self.large_urls[index], save_path, index)
            return save_path, result[0]

    def saveByIndex(self, index: int):
        r18_path = self.r18_dir
        special_tag_path = self.special_tag_subfolder
        if self.type == "ugoira":
            if os.path.exists(Parameters.illust_cache_path + self.getLargeName()):
                path = Parameters.gif_path + r18_path + special_tag_path
                name = path + self.getOriginName()

                makeDir(path)
                shutil.copyfile(Parameters.illust_cache_path + self.getLargeName(), name)
                self.downloaded.update({0: DownloadState.successful})
                self.saveData()
                self.downloaded_path = name
                return {0: DownloadState.successful}
            else:
                self.downloadGif()
                self.saveByIndex(index)
        else:
            path = Parameters.download_path + r18_path + special_tag_path
            makeDir(path)
            if not self.isDownloadedBefore(index):
                name = path + self.getOriginName(index)
                result = self.__tryToDownloadFile(self.urls[index], name, index=index)
                self.downloaded.update({result[1]: result[0]})
                self.saveData()
                self.downloaded_path = name
                return {result[1]: result[0]}

    def saveAll(self, number: Union[int, list] = 0):
        r18_path = self.r18_dir
        special_tag_path = self.special_tag_subfolder
        self.like()
        results = {}

        if self.type == "ugoira":
            if not os.path.exists(Parameters.illust_cache_path + str(self.id) + ".webp"):
                self.downloadGif()
                self.saveAll()

            path = Parameters.gif_path + r18_path + special_tag_path
            makeDir(path)
            name = path + self.getOriginName()
            shutil.copyfile(Parameters.illust_cache_path + str(self.id) + ".webp", name)
            self.downloaded.update({0: DownloadState.successful})
            self.downloaded_path = name
            self.saveData()

        elif self.page_count > 1:
            path = Parameters.group_path + r18_path + special_tag_path + str(self.id) + "\\"
            if type(number) is list or number == 0:
                makeDir(path)

            if number == 0:
                index_list = []
                for i in range(self.page_count):
                    index_list.append(i)
                results = self.downloadListPics(index_list, path)

            elif type(number) is int:
                number -= 1
                if self.isDownloadedBefore(number) or number > self.page_count:
                    raise IndexError("Wrong input index", number)

                name = Parameters.download_path + r18_path + special_tag_path + self.getOriginName(number)
                result = self.__tryToDownloadFile(self.urls[number], name, index=number)
                self.downloaded_path = name
                results.update({result[1]: result[0]})

            elif type(number) is list:
                for i in range(len(number)):
                    number[i] -= 1
                results = self.downloadListPics(number, path)

            else:
                raise TypeError("Wrong input index! Must be a int or a list")

        else:
            # page count is 1
            path = Parameters.download_path + r18_path + special_tag_path
            makeDir(path)
            name = path + self.getOriginName(0)
            result = self.__tryToDownloadFile(self.urls[0], name)
            results.update({result[1]: result[0]})
            self.downloaded_path = name

        self.downloaded.update(results)
        self.saveData()

    def saveAuthHead(self):
        self.__tryToDownloadFile(self.user_head, Parameters.auth_head_path + str(self.user_id) + os.path.splitext(self.user_head)[1])

    def deleteCache(self):
        try:
            os.remove(Parameters.illust_data_path + str(self.id) + Parameters.data_extension)
            os.remove(Parameters.illust_thbnl_path + self.thumbnail_name)
        except FileNotFoundError:
            pass
        print("%d is removed !" % self.id)

    def setName(self, index=0, url='nothing.jpg'):
        """
        index should be a number which begin from 0
        save_type should be "index" or "time"
        """
        if self.type == "ugoira":
            extension = Parameters.gif_extension
        else:
            extension = os.path.splitext(url)[1]

        save_ex = ""
        if Parameters.naming_method == NamingMethod.by_index:
            if self.page_count <= 1:
                save_ex = "0"
            else:
                save_ex = str(index+1)
        elif Parameters.naming_method == NamingMethod.by_time:
            save_ex = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        name = "illust_%d_%s%s" % (self.id, save_ex, extension)
        return name

    def downloadGif(self):
        gif_url = self.gif_url
        delay = self.gif_delay
        gif_name = Parameters.illust_cache_path + str(self.id) + ".webp"
        if os.path.exists(gif_name):
            print(gif_name + "already existed")

        frame_savepath = Parameters.illust_cache_path + str(self.id)
        makeDir(frame_savepath)

        # download & unzip
        self.__tryToDownloadFile(gif_url, frame_savepath + ".zip")
        try:
            with zipfile.ZipFile(frame_savepath + ".zip", 'r') as zip_ref:
                zip_ref.extractall(frame_savepath)
        except FileNotFoundError:
            print("frames of %d dowmload failed")
            return gif_name

        # compose to gif
        image = []
        for root, dirs, file in os.walk(frame_savepath + '\\'):
            for name in file:
                img_array = iio.imread(root + name)
                try:
                    img_array.shape[2]

                except IndexError:
                    img2 = np.zeros((img_array.shape[0], img_array.shape[1], 3)).astype(np.uint8)
                    for i in range(3):
                        img2[:, :, i] = img_array
                    img_array = img2
                image.append(img_array)

        image = np.array(image)
        iio.imwrite(gif_name, image, duration=delay, kmax=1)

        # delete cache
        os.remove(frame_savepath + ".zip")
        shutil.rmtree(frame_savepath, ignore_errors=True)

        print('composing to gif successfully')
        return gif_name

    def downloadListPics(self, index_list: list, path: str):
        results = {}
        for i in index_list:
            if i >= self.page_count:
                raise IndexError("Wrong input index: ", i+1)
        for count in range(math.ceil(len(index_list) / Parameters.max_download_thread)):
            que = Queue()
            thread_list = []

            for index_count in range(Parameters.max_download_thread):
                index = index_count + count * Parameters.max_download_thread
                if index >= len(index_list):
                    break
                if not self.isDownloadedBefore(index_list[index]):
                    thread = threading.Thread(target=lambda q, arg1, arg2, arg3: q.put(self.__tryToDownloadFile(arg1, arg2, index=arg3)),
                                              args=(que, self.urls[index_list[index]], path + self.getOriginName(index_list[index]),
                                                    index_list[index]))
                    thread_list.append(thread)
                    thread.start()
                    time.sleep(2)
                # print(threading.activeCount())
                # self.__try_to_download_file(self.urls[index], path + self.set_name(self.urls[index]))
            for thread in thread_list:
                thread.join()

            while not que.empty():
                result = que.get()
                results.update({result[1]: result[0]})
        self.downloaded_path = path
        return results

    def __tryToDownloadFile(self, url, save_path, i=0, index=0):
        if i < 2:
            try:
                self.__downloadFile(url, save_path)
            except Exception as e:
                if type(e) is InterruptError or type(e) is CannotVerifyError:
                    i = i + 1
                    print("download file: %d was unexpectedly interrupted, retry..." % self.id)
                    try:
                        os.remove(save_path)
                    except FileNotFoundError:
                        pass
                    delay_time = random.randint(1, 3)
                    time.sleep(delay_time)
                    self.__tryToDownloadFile(url, save_path, i)
                elif type(e) is FileExistsError:
                    pass
                    # print("%d is already existed" % self.id)
            else:
                delay_time = random.randint(0, 3)
                time.sleep(delay_time)
        else:
            try:
                self.__downloadFile(url, save_path)
            except InterruptError:
                return DownloadState.failed, index
            except CannotVerifyError:
                return DownloadState.cannot_verify, index
            except Exception as e:
                print(e)
                return DownloadState.unexpected_error, index

        return DownloadState.successful, index

    def __downloadFile(self, url, save_path):
        """
        it will raise:
        Interrupt error
        Cannot verify error
        exception that is not predictable
        """
        headers = {'Referer': 'https://app-api.pixiv.net/'}
        if self.checkExisted(save_path):
            raise FileExistsError("File already exist")

        try:
            with requests.get(url, headers=headers, proxies=Parameters.proxies, stream=True) as response, open(save_path, 'wb') as file:
                shutil.copyfileobj(response.raw, file)
        except Exception as e:
            raise InterruptError(f'Download {self.id} was unexpectedly interrupted.\n error type : {type(e)}')

        try:
            expected_length = response.headers['Content-Length']
        except KeyError:
            raise CannotVerifyError('Cannot verify file: %d, please check it manually' % self.id)
        except Exception as e:
            print(f"An unknown error occured, but continue. Error type: {type(e)}, illust id is {self.id}")
            raise e

        actual_length = str(os.path.getsize(save_path))
        if expected_length != actual_length:
            raise InterruptError('Download %d was unexpectedly interrupted.' % self.id)
            # print("Download %d successfully!" % self.id)

        return 0

    def like(self):
        try:
            api.illust_bookmark_add(self.id)
        except Exception as e:
            print(f"like failed,\ntype is {type(e)},\nplease retry")
        else:
            self.is_like = True
            self.saveData()

    def cancelLike(self):
        api.illust_bookmark_delete(self.id)
        self.is_like = False
        self.saveData()

    def locateSavePath(self):
        try:
            path = self.getSavePath().encode().decode("utf-8")
        except FileNotFoundError:
            raise FileNotFoundError
        else:
            print(path)
            if os.path.exists(path):
                subprocess.Popen("explorer /select," + path)

    def saveData(self):
        self.saveAuthHead()
        data_path = Parameters.illust_data_path + str(self.id) + Parameters.data_extension
        if not os.path.exists(data_path):
            with open(data_path, 'x'):
                # just create a file
                pass
        with open(data_path, 'wb') as save_path:
            pickle.dump(self, save_path)

    def readCustomData(self):
        with open(Parameters.illust_data_path + str(self.id) + Parameters.data_extension, 'rb') as save_path:
            try:
                instance: Illust = pickle.load(save_path)
            except pickle.UnpicklingError as e:
                print(f"{e} error occurred in {save_path}")
                raise e
            else:
                self.downloaded_path = instance.downloaded_path
                self.downloaded = instance.downloaded
                self.need_thumbnail = instance.need_thumbnail

    def __str__(self):
        string = f"Illust name: {self.title}, id: {self.id}\nIllust tag:{self.tags, self.translate_tags}\n"
        return string


class SaveDataWorker(threading.Thread):
    def __init__(self, queue):
        super(SaveDataWorker, self).__init__()
        self.illust = Illust
        self.q = queue
        self.start()

    def run(self):
        while True:
            if self.q.empty():
                break
            self.illust = self.q.get()
            print("get illust %s data" % self.illust.title)
            try:
                self.illust.saveData()
            except Exception as e:
                print(self.illust.id, f"saving failed, error type{type(e), e} ")
            self.q.task_done()


class SaveTWorker(threading.Thread):
    def __init__(self, queue):
        super(SaveTWorker, self).__init__()
        self.q = queue
        self.start()

    def run(self):
        while True:
            if self.q.empty():
                break
            illust: Illust
            illust = self.q.get()
            print("save thumbnails illust %s" % illust.title)
            if illust.need_thumbnail:
                illust.saveThumbnail()
            self.q.task_done()


def loadID(illust_id):
    with open(Parameters.illust_data_path + str(illust_id) + Parameters.data_extension, 'rb') as save_path:
        try:
            instance = pickle.load(save_path)
        except pickle.UnpicklingError as e:
            print(f"{e} error occurred in {save_path}")
            raise e
        return instance


def loadIllustDataByPath(path: str) -> Illust:
    with open(path, 'rb') as save_path:
        try:
            data = pickle.load(save_path)
        except pickle.UnpicklingError as e:
            print(f"load file: \n{path}\n failed, error: \n{e}")
            raise e
    return data


def getIllustByID(illust_id: int) -> Illust:
    return Illust(api.illust_detail(illust_id).illust)


def removeObjInList(lst: list, o: object):
    for _ in range(len(lst)):
        try:
            lst.remove(o)
        except ValueError:
            continue
    return lst


def getSpecialTags():
    global special_tags_sort
    global special_tags_dict

    tag_dict = {}
    tag_sort = []
    with open(Parameters.special_tags_config_path, "rb") as config_file:
        config_file_string = config_file.read().decode("utf-8")

    tag_dict_str_list = removeObjInList(config_file_string.split("\r\n"), "")

    for tag_dict_str in tag_dict_str_list:
        tag_dict_value, tag_dict_key = tag_dict_str.split(" : ")
        tag_dict_key_list = removeObjInList(tag_dict_key.split(" "), "")
        tag_sort.append(tag_dict_value)
        for key in tag_dict_key_list:
            tag_dict.update({key: tag_dict_value})

    special_tags_sort = tag_sort
    special_tags_dict = tag_dict
    print("get all special tags:\n", special_tags_sort)

    return tag_dict, tag_sort


def saveAllData():
    count = 0
    total = 0
    json_result_follow_new = api.illust_follow()
    illust_q = queue.Queue()
    while True:
        try:
            for illust in json_result_follow_new.illusts:
                illust = Illust(illust)
                if illust.block:
                    continue
                illust_q.put(illust)
                total += 1
                # illust.save_data()
                if illust.is_like:
                    count = count + 1
                if count >= 3:
                    break
        except TypeError:
            break

        if count >= 3:
            break
        next_qs = api.parse_qs(json_result_follow_new.next_url)
        try:
            json_result_follow_new = api.illust_follow(**next_qs)
        except TypeError:
            print("hit end")
            break

    print("\n---get list done---\ntotal %d pics update\n" % total)
    for i in range(10):
        SaveDataWorker(illust_q)
    print(illust_q.qsize())
    illust_q.join()


def loadAll():
    global illust_list
    for file in os.listdir(Parameters.illust_data_path):
        if os.path.splitext(file)[1] == Parameters.data_extension:
            illust = loadID(int(os.path.splitext(file)[0]))
            # print(illust.title, illust.create_time.strftime("%Y年%m月%d日%H时%M分%S秒 创建"))
            if illust.need_thumbnail:
                illust_list.append(illust)
    print("total count %d" % len(illust_list))
    return illust_list


def loadAllNSFW():
    global illust_list
    print("read data")
    for file in os.listdir(Parameters.illust_data_path):
        if os.path.splitext(file)[1] == Parameters.data_extension:
            illust = loadID(int(os.path.splitext(file)[0]))
            if illust.need_thumbnail:
                if Parameters.nsfw == NSFWState.sfw and illust.is_nsfw:
                    continue
                elif Parameters.nsfw == NSFWState.nsfw and not illust.is_nsfw:
                    continue
            illust_list.append(illust)

    print("total count %d" % len(illust_list))
    return illust_list


def loadAllID():
    id_list = []
    for file in os.listdir(Parameters.illust_data_path):
        if os.path.splitext(file)[1] == Parameters.data_extension:
            illust = int(os.path.splitext(file)[0])
            print(type(illust))
            id_list.append(illust)
    print("total count %d" % len(id_list))
    return id_list


def deleteLiked(data_list: list):
    count = 0
    for illust in reversed(data_list):
        print(illust.id, illust.is_like)
        if illust.is_like:
            count = count + 1
        if count >= 3 and illust.is_like:
            illust.deleteCache()
            data_list.remove(illust)
    for name in os.listdir(Parameters.illust_thbnl_path):
        file_name = os.path.splitext(name)[0]
        if not os.path.exists(Parameters.illust_data_path + file_name + Parameters.data_extension):
            os.remove(Parameters.illust_thbnl_path + name)
    return data_list


def deleteAllLikedIllust():
    deleteLiked(loadAll())


def saveThumbnails():
    illust_q = queue.Queue()

    saveAllData()
    data_list = loadAll()
    # data_list = delete_liked(data_list)
    print("\n---save thumbnails---\n")
    for illust in data_list:
        illust_q.put(illust)
    for i in range(8):
        SaveTWorker(illust_q)
        time.sleep(0.3)
    illust_q.join()


def deleteAllSavedData():
    if os.path.exists(Parameters.illust_data_path):
        print("removing data path", os.path.abspath(Parameters.illust_data_path))
        shutil.rmtree(Parameters.illust_data_path)
    if os.path.exists(Parameters.illust_thbnl_path):
        print("removing thumbnail path", os.path.abspath(Parameters.illust_thbnl_path))
        shutil.rmtree(Parameters.illust_thbnl_path)
    if os.path.exists(Parameters.illust_cache_path):
        print("removing cache path", os.path.abspath(Parameters.illust_cache_path))
        shutil.rmtree(Parameters.illust_cache_path)


def createAcquiredPaths():
    path_list = Parameters.path_list
    for folder_path in path_list:
        makeDir(folder_path)


def getLoginToken():
    with open(Parameters.login_token_path, "rb") as file:
        login_token = file.read().decode("utf-8")
    return login_token


def login():
    global api
    # login with token
    api.auth(refresh_token=getLoginToken())
    print("login successfully")
    # return api


def setLanguage(lang):
    global api
    api.set_accept_language(lang)


def sleep(sec):
    time.sleep(sec)


def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


'''##############################    START   #############   HERE    ############################################'''

api = pixiv.AppPixivAPI(proxies=Parameters.proxies)
illust_list = []
special_tags_dict = {}
special_tags_sort = []
getSpecialTags()
