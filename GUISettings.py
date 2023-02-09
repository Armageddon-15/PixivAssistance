"""
settings for gui
"""
import json


class SettingValue:
    def __init__(self, va):
        self.__value = va

    def setValue(self, va):
        self.__value = va

    def getValue(self):
        return self.__value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, va):
        self.__value = va

    def __add__(self, other):
        return other + self.__value

    def __radd__(self, other):
        return self.__value + other

    def __iadd__(self, other):
        return self.__value + other

    def __sub__(self, other):
        return self.__value - other

    def __rsub__(self, other):
        return other - self.__value

    def __isub__(self, other):
        return self.__value - other

    def __mul__(self, other):
        return other * self.__value

    def __rmul__(self, other):
        return other * self.__value

    def __imul__(self, other):
        return other * self.__value

    def __truediv__(self, other):
        return self.__value / other

    def __rtruediv__(self, other):
        return other / self.__value

    def __idiv__(self, other):
        return self.__value / other

    def __floordiv__(self, other):
        return self.__value // other

    def __rfloordiv__(self, other):
        return other // self.__value

    def __ifloordiv__(self, other):
        return self.__value // other

    def __mod__(self, other):
        return self.__value % other

    def __rmod__(self, other):
        return other % self.__value

    def __imod__(self, other):
        return self.__value % other

    def __lt__(self, other):
        return self.__value < other

    def __le__(self, other):
        return self.__value <= other

    def __eq__(self, other):
        return self.__value == other

    def __ne__(self, other):
        return self.__value != other

    def __gt__(self, other):
        return self.__value > other

    def __ge__(self, other):
        return self.__value >= other

    def __int__(self):
        return int(self.__value)

    # def __str__(self):
    #     return str(self.__value)


class BaseSetting:
    def toJson(self):
        d = {}
        for key in self.__dict__.keys():
            d.update({key: self.__dict__[key].getValue()})
        return d

    def toAttribute(self, json_dict):
        for key in self.__dict__.keys():
            self.__dict__[key].setValue(json_dict[key].getValue())


'''Pixiv Assistance'''


# detail
class Detail(BaseSetting):
    def __init__(self):
        self.btn_size = SettingValue(41)
        self.author_head_icon_size = SettingValue(70)
        self.author_name_font_size = SettingValue(16)
        self.tag_font_size = SettingValue(15)
        self.translate_tag_font_size = SettingValue(11)
        self.tag_sharp_size = SettingValue(20)
        self.tags_per_line = SettingValue(1)
        self.tag_spacing = SettingValue(0)
        self.time_font_size = SettingValue(11)
        self.description_font_size = SettingValue(13)
        self.stream_per_load = SettingValue(4)
        self.scroll_step = SettingValue(500)


# explore
class Explore(BaseSetting):
    def __init__(self):
        self.illust_title_font_size = SettingValue(25)
        self.count_font_size = SettingValue(30)
        self.ai_font_size = SettingValue(20)
        self.state_font_size = SettingValue(11)
        self.btn_size = SettingValue(50)
        self.gif_icon_size = SettingValue(100)
        self.thumbnail_size = SettingValue(360)
        self.thumbnail_spacing = SettingValue(5)
        self.scroll_step = SettingValue(366)
        self.pic_per_page = SettingValue(50)


# window
class Window(BaseSetting):
    def __init__(self):
        self.use_this = SettingValue(False)
        self.x = SettingValue(0)
        self.y = SettingValue(0)
        self.width = SettingValue(1000)
        self.height = SettingValue(800)

    def setGeo(self, x, y, width, height):
        self.x = SettingValue(x)
        self.y = SettingValue(y)
        self.width = SettingValue(width)
        self.height = SettingValue(height)


class MainWindow(BaseSetting):
    def __init__(self):
        self.head_icon_size = SettingValue(80)
        self.head_icon_path = SettingValue("icons\\04.png")
        self.grip_size = SettingValue(8)
        self.title_font_size = SettingValue(18)
        self.illust_title_font_size = SettingValue(14)
        self.operate_btn_size = SettingValue(32)


def saveSettings():
    global a_dict
    a_dict = {"window": win_setting.toJson(),
              "detail": detail_setting.toJson(),
              "explore": explore_setting.toJson(),
              "main": main_setting.toJson()}

    with open("GUI_Setting.json", "w") as json_file:
        json.dump(a_dict, json_file, indent=4)


def readSettings():
    global detail_setting, explore_setting, win_setting, a_dict
    with open("GUI_Setting.json", "r") as json_file:
        a_dict = json.load(json_file)
        for setting_class in a_dict.keys():
            for setting in a_dict[setting_class].keys():
                a_dict[setting_class][setting] = SettingValue(a_dict[setting_class][setting])

    win_setting.toAttribute(a_dict["window"])
    detail_setting.toAttribute(a_dict["detail"])
    explore_setting.toAttribute(a_dict["explore"])
    main_setting.toAttribute(a_dict["main"])


def saveAndLoad():
    saveSettings()
    readSettings()


detail_setting = Detail()
explore_setting = Explore()
main_setting = MainWindow()
win_setting = Window()

a_dict = dict()

try:
    readSettings()
except json.decoder.JSONDecodeError:
    saveAndLoad()
except KeyError:
    saveAndLoad()
