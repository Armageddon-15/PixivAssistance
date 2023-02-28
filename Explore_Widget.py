from PyQt6.QtWidgets import QLabel, QPushButton, QMenu, QWidget, QGridLayout, QVBoxLayout, QFrame, QHBoxLayout
from PyQt6.QtWidgets import QSizePolicy, QSpinBox, QAbstractSpinBox
from PyQt6.QtGui import QFont, QIcon, QImage, QPixmap, QDrag
from PyQt6.QtCore import Qt, QSize, QRect, QThread, QPoint, QMimeData
from PyQt6 import QtCore
import Parameters
from ScrollAreaWithStepSettings import ScrollAreaWithStepSettings
from Illust_reader import IllustReader
from PAEnum import *

import GUISettings
import Illust
import math
import webbrowser
import numpy as np


class GetKeyGrabber(QThread):
    def __init__(self):
        super(GetKeyGrabber, self).__init__()

    def run(self):
        while True:
            print(QWidget.keyboardGrabber())
            Illust.sleep(1)


class DownloadThread(QThread):
    update = QtCore.pyqtSignal(str)

    def __init__(self, illust: Illust.Illust = None, add_func=None):
        super().__init__()
        self.illust = illust
        self.add_func = add_func

    def run(self):
        self.update.emit("Downloading")
        try:
            self.illust.saveAll()
            state = self.illust.downloaded
        except Exception as e:
            print(f"Download Error Occurred, type is {type(e)}")
        else:
            print(self.illust.id, state)
            value = Illust.removeObjInList(list(state.values()), DownloadState.successful)
            if len(value) != 0:
                if len(value) < len(list(state.values())):
                    self.update.emit("Not all successful")
                elif len(value) == len(list(state.values())):
                    self.update.emit("All failed")
            else:
                self.update.emit("Successful")
            if self.add_func is not None:
                self.add_func(self.illust.page_count - len(value), 0)


class LikeIllustThread(QThread):
    over = QtCore.pyqtSignal(Illust.Illust)

    def __init__(self, illust: Illust.Illust = None):
        super(LikeIllustThread, self).__init__()
        self.illust = illust

    def run(self) -> None:
        if self.illust.is_like:
            self.illust.cancelLike()
            print("Cancel like illust", self.illust.id)
        else:
            self.illust.like()
            print("Like illust", self.illust.id)
        self.over.emit(self.illust)


# clickable label for pic
class Thumbnails(QLabel):
    def __init__(self, widget):
        super(Thumbnails, self).__init__(widget)
        self.main = widget
        self.illust = None
        self.index = 0
        self.illust_name = ""
        self.isgif = False
        self.is_like = False
        self.page_count = 1
        # self.nsfw = NSFWState.all
        self.download_text = ""
        self.hover = False
        self.data_viewer = IllustReader()
        self.setScaledContents(True)

        self.download_worker = DownloadThread()
        self.like_worker = LikeIllustThread()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.tags = []

        self.gif = QLabel(self)
        self.gif.setScaledContents(True)
        self.gif.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.gif.setFont(QFont("Microsoft JhengHei", 50, 0, False))
        self.gif.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_text = QLabel(self)
        self.name_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_text.setStyleSheet("color : rgb(200, 200, 200); background-color : rgba(0, 0, 0, 0)")
        self.name_text.raise_()
        # self.name_text.setMinimumSize(100, 100)
        self.name_text.setWordWrap(True)

        self.count_text = QLabel(self)
        self.count_text.raise_()
        self.count_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.like_btn = QPushButton(self)
        self.like_btn.setIcon(QIcon("icons\\like.png"))
        self.like_btn.raise_()
        self.like_btn.setFlat(True)
        self.like_btn.setFont(QFont("Microsoft JhengHei", 25, 0, False))
        self.like_btn.clicked.connect(self.click_like_btn)

        self.like_dl_btn = QPushButton(self)
        self.like_dl_btn.setIcon(QIcon("icons\\like_dl.png"))
        self.like_dl_btn.raise_()
        self.like_dl_btn.setFlat(True)
        self.like_dl_btn.setFont(QFont("Microsoft JhengHei", 25, 0, False))
        self.like_dl_btn.clicked.connect(self.click_like_dl_btn)
        self.setMinimumSize(GUISettings.explore_setting.thumbnail_size, GUISettings.explore_setting.thumbnail_size)
        self.setMaximumSize(GUISettings.explore_setting.thumbnail_size, GUISettings.explore_setting.thumbnail_size)

        self.ai_label = QLabel(self)
        self.ai_label.setAlignment(Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)
        self.ai_label.setStyleSheet("color : rgb(180, 20, 20); background-color : rgba(0, 0, 0, 25)")
        self.ai_label.raise_()

        self.download_state_label = QLabel(self)
        self.download_state_label.setStyleSheet("color : rgb(200, 200, 200); background-color : rgba(0, 0, 0, 0)")
        self.download_state_label.raise_()
        self.download_state_label.setText("")

        self.runtimeUpdate()
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.download_state_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

    def loadAttr(self, illust):
        self.illust = illust
        self.illust_name = illust.title
        self.getPageCount(illust)
        self.getLike(illust.is_like)
        self.getAiType(illust)
        # self.tags = illust.tags
        if illust.type == "ugoira":
            self.isgif = True

    def getAiType(self, illust: Illust.Illust):
        for tag in illust.tags:
            if tag == "AI生成":
                self.ai_label.setText("AI")
                return 0
        self.ai_label.setStyleSheet("color : rgb(180, 20, 20); background-color : rgba(0, 0, 0, 0)")

    def getPageCount(self, illust):
        self.page_count = illust.page_count
        if self.page_count > 1:
            self.count_text.setText(str(self.page_count))
            self.count_text.setStyleSheet("color : white ;background-color: rgba(0, 0, 0, 150)")
        else:
            self.count_text.setStyleSheet("color : white ;background-color: rgba(0, 0, 0, 0)")

    def getLike(self, s: bool):
        self.is_like = s
        if self.is_like:
            self.like_btn.setIcon(QIcon("icons\\liked.png"))
            self.like_dl_btn.setIcon(QIcon("icons\\liked_dl.png"))
        else:
            self.like_btn.setIcon(QIcon("icons\\like.png"))
            self.like_dl_btn.setIcon(QIcon("icons\\like_dl.png"))

    def setDownloadState(self, string: str):
        self.download_text = string
        self.download_state_label.setText(string)
        # if string == "Successful":
        #     self.main.setDownloadState(self.illust.page_count, 0)
        # print(self.download_text)

    def rematch(self):
        size = GUISettings.explore_setting.count_font_size*1.8
        page_count_constrain = QRect(self.size().width() - size, 0, size, size)
        self.count_text.setGeometry(page_count_constrain)

        btn_constrain = QRect(self.size().width() - GUISettings.explore_setting.btn_size*2 - 3, self.size().height() - GUISettings.explore_setting.btn_size - 3,
                              GUISettings.explore_setting.btn_size, GUISettings.explore_setting.btn_size)
        self.like_btn.setGeometry(btn_constrain)

        btn2_constrain = QRect(self.size().width() - GUISettings.explore_setting.btn_size - 3, self.size().height() - GUISettings.explore_setting.btn_size - 3,
                               GUISettings.explore_setting.btn_size, GUISettings.explore_setting.btn_size)
        self.like_dl_btn.setGeometry(btn2_constrain)

        if self.isgif:
            self.gif.setPixmap(set_pixmap('icons\\gif.png'))
            gif_constrain = QRect(int((self.size().width() - GUISettings.explore_setting.gif_icon_size) / 2),
                                  int((self.size().height() - GUISettings.explore_setting.gif_icon_size) / 2),
                                  GUISettings.explore_setting.gif_icon_size, GUISettings.explore_setting.gif_icon_size)
            self.gif.setGeometry(gif_constrain)

        self.name_text.setFixedSize(self.size().width(), self.size().height())

    def click_like_btn(self):
        self.like_worker = LikeIllustThread(self.illust)
        self.like_worker.over.connect(self.loadAttr)
        self.like_worker.start()

    def click_like_dl_btn(self):
        self.download_worker = DownloadThread(self.illust, self.main.setDownloadState)
        self.download_worker.update.connect(self.setDownloadState)
        self.download_worker.start()
        self.download_worker.finished.connect(self.load_mt)
        self.main.setDownloadState(0, self.illust.page_count)
        print("like and download %d picture" % self.index)

    def load_mt(self):
        self.loadAttr(self.illust)

    def runtimeUpdate(self):
        # in fact, it will be created when main's runtime update be executed
        self.name_text.setFont(QFont("Microsoft JhengHei", GUISettings.explore_setting.illust_title_font_size.value, 0, False))
        font = QFont("Microsoft JhengHei", GUISettings.explore_setting.count_font_size.value, 0, False)
        font.setBold(True)
        self.count_text.setFont(font)
        font.setPointSize(GUISettings.explore_setting.ai_font_size.value)
        self.ai_label.setFont(font)
        self.download_state_label.setFont(QFont("Microsoft JhengHei", GUISettings.explore_setting.state_font_size.value, 0, False))

        self.ai_label.setFixedSize(GUISettings.explore_setting.ai_font_size.value*2, GUISettings.explore_setting.ai_font_size.value*2)
        self.like_btn.setIconSize(QSize(GUISettings.explore_setting.btn_size.value, GUISettings.explore_setting.btn_size.value))
        self.like_dl_btn.setIconSize(QSize(GUISettings.explore_setting.btn_size.value, GUISettings.explore_setting.btn_size.value))

        self.rematch()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.MiddleButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(str(self.illust.id))
            drag.setMimeData(mime_data)

            pixmap = self.pixmap()
            pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            qimg = pixmap.toImage()
            qimg.convertToFormat(QImage.Format.Format_RGBA8888)
            ptr = qimg.bits()
            ptr.setsize(qimg.width()*qimg.height()*4)
            array = np.array(ptr).reshape(qimg.height(), qimg.width(), 4)
            array = array[:, :, [2, 1, 0, 3]]
            # breakpoint()
            array = np.uint8(np.float32(array) * 0.7)
            new_qimg = QImage(array.tobytes(), qimg.width(), qimg.height(), QImage.Format.Format_RGBA8888)
            drag.setPixmap(QPixmap.fromImage(new_qimg))
            drop_action = drag.exec()

    def mouseReleaseEvent(self, e) -> None:
        global_pos_TL = self.mapToGlobal(QPoint(0, 0))
        global_pos_BR = self.mapToGlobal(QPoint(self.size().width(), self.size().height()))
        cursor_pos = e.globalPosition().toPoint()

        if e.button() == Qt.MouseButton.LeftButton:
            if global_pos_TL.x() < cursor_pos.x() < global_pos_BR.x() and global_pos_TL.y() < cursor_pos.y() < global_pos_BR.y():
                print("click %s, index : %d" % (self.illust_name, self.index))
                self.main.toDetailPage(self.illust, self.index - 1)

    def resizeEvent(self, e):
        self.rematch()

    def enterEvent(self, e):
        self.name_text.setText(self.illust_name)
        self.name_text.setStyleSheet("color : white ;background-color: rgba(0, 0, 0, 120);")
        self.download_state_label.setText(self.download_text)
        self.hover = True
        # print("Entered %d" % self.index)

    def leaveEvent(self, e):
        self.name_text.setText("")
        self.name_text.setStyleSheet("color : rgb(200, 200, 200);background-color: rgba(0, 0, 0, 0);")
        if self.download_text != "Downloading":
            self.download_state_label.setText("")
        # print("Left %d" % self.index)
        self.hover = False

    def contextMenuEvent(self, e):
        cmenu = QMenu(self)
        to_web = cmenu.addAction("To Browser")
        update = cmenu.addAction("Update")
        locate_path = cmenu.addAction("Locate Saved Path")
        read_data = cmenu.addAction("Show Illust Data")

        action = cmenu.exec(self.mapToGlobal(e.pos()))
        if action == to_web:
            url = "https://www.pixiv.net/artworks/%d" % self.illust.id
            webbrowser.open(url, 2)
        elif action == update:
            self.illust.updateIllust()
            self.loadAttr(self.illust)
        elif action == locate_path:
            try:
                self.illust.locateSavePath()
            except FileNotFoundError:
                print(f"{self.illust.id} is not saved")
        elif action == read_data:
            self.data_viewer = IllustReader(illust=self.illust)
            self.data_viewer.show()


class PicGrid(QWidget):
    def __init__(self, widget):
        super().__init__(widget)
        self.main = widget
        self.page_count = 0
        self.illust_list = list(reversed(Illust.loadByOption()))
        self.max_page_count = math.ceil(len(self.illust_list) / GUISettings.explore_setting.pic_per_page.value)

        self.gbox = QGridLayout(self)
        self.gbox.setContentsMargins(0, 0, 0, 0)
        self.vbox = QVBoxLayout(self)

        self.curr_pic_boxes = []
        self.createGrid()
        self.frame = QFrame()
        self.frame2 = QFrame()
        size_policy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        self.frame.setSizePolicy(size_policy)

        size_policy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(1)
        size_policy.setVerticalStretch(1)
        self.frame2.setSizePolicy(size_policy)

        self.vbox.addLayout(self.gbox)
        self.vbox.addWidget(self.frame)
        self.hbox = QHBoxLayout(self)
        self.hbox.addLayout(self.vbox)
        self.hbox.addWidget(self.frame2)
        self.setLayout(self.gbox)

    def createGrid(self):
        self.setPageCount()
        self.curr_pic_boxes.clear()
        max_num = GUISettings.explore_setting.pic_per_page.value
        for box_num in range(self.page_count*max_num, (self.page_count + 1) * max_num):
            try:
                self.loadPicBox(box_num)
            except IndexError:
                break
        self.layoutPicBox(self.size(), QSize(0, 0))

    def layoutPicBox(self, new_size, old_size):
        new_column = int((new_size.width()-30-6*old_size.width()/GUISettings.explore_setting.thumbnail_size)
                         / GUISettings.explore_setting.thumbnail_size)
        new_column = max(new_column, 1)
        old_column = int((old_size.width()-30-6*old_size.width()/GUISettings.explore_setting.thumbnail_size)
                         / GUISettings.explore_setting.thumbnail_size)

        if new_column != old_column:
            for i in reversed(range(0, self.gbox.count())):
                self.gbox.itemAt(i).widget().hide()
                self.gbox.removeWidget(self.gbox.itemAt(i).widget())

            for pic_box in self.curr_pic_boxes:
                index = pic_box.index - 1 - (GUISettings.explore_setting.pic_per_page.value * self.page_count)
                r = int(index / new_column)
                self.gbox.setColumnStretch(index % new_column, 0)
                self.gbox.setRowStretch(r, 1)
                self.gbox.addWidget(pic_box, r, index % new_column)

            for i in reversed(range(0, self.gbox.count())):
                self.gbox.itemAt(i).widget().show()

    def loadPicBox(self, box_num):
        pic_box = Thumbnails(self)
        try:
            pic_box.setPixmap(set_pixmap(Parameters.illust_thbnl_path + self.illust_list[box_num].thumbnail_name))
            pic_box.loadAttr(self.illust_list[box_num])
        except IndexError:
            pic_box.deleteLater()
            self.main.isBottom()
            raise IndexError
        pic_box.index = box_num + 1
        self.curr_pic_boxes.append(pic_box)

    def nextPage(self):
        self.toCertainPage(self.page_count + 1)

    def prePage(self):
        self.toCertainPage(self.page_count - 1)

    def toCertainPage(self, page: int):
        self.page_count = min(max(0, page), self.max_page_count-1)
        self.main.isNormal()
        self.createGrid()

    def setPageCount(self):
        self.main.setPageCount(str(self.page_count + 1),  str(self.max_page_count))
        if self.page_count <= 0:
            self.main.isTop()
        if self.page_count >= self.max_page_count:
            self.main.isBottom()

    def toDetailPage(self, illust, index):
        self.main.toDetailPage(illust, index)

    def setDownloadState(self, download=0, total=0):
        self.main.setDownloadState(download, total)

    def runtimeUpdate(self):
        self.max_page_count = math.ceil(len(self.illust_list) / GUISettings.explore_setting.pic_per_page.value)
        self.page_count = min(self.page_count, self.max_page_count-1)
        self.createGrid()
        self.gbox.setSpacing(GUISettings.explore_setting.thumbnail_spacing.value)


class PageCountLabel(QFrame):
    def __init__(self, parent):
        super(PageCountLabel, self).__init__(parent)
        self.main = parent
        self.l_frame = QFrame(self)
        self.page_count_edit = QSpinBox(self)
        self.slash_label = QLabel(self)
        self.max_label = QLabel(self)
        self.r_frame = QFrame(self)

        self.page_count_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.page_count_edit.setStyleSheet("border: 0px")
        self.page_count_edit.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.page_count_edit.setMaximum(9999)
        self.slash_label.setText("/")
        self.slash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.max_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.l_frame)
        self.hbox.addWidget(self.page_count_edit)
        self.hbox.addWidget(self.slash_label)
        self.hbox.addWidget(self.max_label)
        self.hbox.addWidget(self.r_frame)

    def setText(self, count: str, max_page_count: str):
        self.page_count_edit.setValue(int(count))
        self.max_label.setText(max_page_count)

    def getTypeInPage(self):
        return self.page_count_edit.value()

    def toCertainPage(self):
        self.main.toCertainPage()

    def keyPressEvent(self, event) -> None:
        if event.key() != 0:
            if event.key() == 16777220 or event.key() == 16777221:
                self.toCertainPage()


class ExploreWidget(QWidget):
    def __init__(self, widget):
        super(ExploreWidget, self).__init__(widget)
        self.main = widget
        self.scroll_value = 0

        # set page count frame
        self.page_count_frame = QFrame(self)
        self.page_count_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.pc_left_frame = QFrame(self.page_count_frame)
        self.pc_left_frame.setFrameShape(QFrame.Shape.NoFrame)

        self.pre_button = QPushButton(self.page_count_frame)
        self.pre_button.setMinimumSize(150, 0)
        self.pre_button.clicked.connect(self.prePage)
        self.pre_button.setStyleSheet("border-radius: 5px;border: 1px solid black;")
        self.pre_button.setFont(QFont("Microsoft JhengHei", 12, 0, False))
        self.pre_button.setText("previous page")

        self.page_count_label = PageCountLabel(self)

        self.next_button = QPushButton(self.page_count_frame)
        self.next_button.setMinimumSize(150, 0)
        self.next_button.clicked.connect(self.nextPage)
        self.next_button.setStyleSheet("border-radius: 5px;border: 1px solid black;")
        self.next_button.setFont(QFont("Microsoft JhengHei", 12, 0, False))
        self.next_button.setText("next page")

        self.pc_right_frame = QFrame(self.page_count_frame)
        self.pc_right_frame.setFrameShape(QFrame.Shape.NoFrame)
        # layout page count frame
        self.page_count_frame_hbox = QHBoxLayout(self.page_count_frame)
        self.page_count_frame_hbox.addWidget(self.pc_left_frame)
        self.page_count_frame_hbox.addWidget(self.pre_button)
        self.page_count_frame_hbox.addWidget(self.page_count_label)
        self.page_count_frame_hbox.addWidget(self.next_button)
        self.page_count_frame_hbox.addWidget(self.pc_right_frame)
        self.widget = QWidget(self)
        self.setMinimumSize(GUISettings.explore_setting.thumbnail_size+50, GUISettings.explore_setting.thumbnail_size+50)
        self.explore_scrollArea = ScrollAreaWithStepSettings(self.widget)
        self.explore_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.explore_scrollArea.setWidgetResizable(True)
        self.explore_scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.explore_scrollArea.setStyleSheet(open("ScrollBar.qss").read())
        self.explore_content_widget = PicGrid(self)

        self.runtimeUpdate()

        # layout
        self.excw_vbox = QVBoxLayout(self.explore_scrollArea)
        self.excw_vbox.addWidget(self.explore_content_widget, 0, Qt.AlignmentFlag.AlignCenter)
        self.excw_vbox.setContentsMargins(0, 0, 100, 0)
        self.explore_scrollArea.setWidget(self.explore_content_widget)

        self.exs_vbox = QVBoxLayout(self.widget)
        self.exs_vbox.setSpacing(0)
        self.exs_vbox.setContentsMargins(0, 0, 0, 0)
        self.exs_vbox.addWidget(self.explore_scrollArea)
        self.exs_vbox.addWidget(self.page_count_frame)
        self.setLayout(self.exs_vbox)

    def isBottom(self):
        self.next_button.setEnabled(False)

    def isTop(self):
        self.pre_button.setEnabled(False)

    def isNormal(self):
        self.pre_button.setEnabled(True)
        self.next_button.setEnabled(True)

    def nextPage(self):
        self.explore_content_widget.nextPage()
        self.explore_scrollArea.toTop()

    def prePage(self):
        self.explore_content_widget.prePage()
        self.explore_scrollArea.toTop()

    def toCertainPage(self):
        self.explore_content_widget.toCertainPage(self.page_count_label.getTypeInPage()-1)
        self.explore_scrollArea.toTop()

    def setPageCount(self, count, m):
        self.page_count_label.setText(count, m)

    def toDetailPage(self, illust, index):
        self.main.toDetailPage(illust, index)

    def setDownloadState(self, downloading=0, total=0):
        self.main.setDownloadState(downloading, total)

    def runtimeUpdate(self):
        self.explore_scrollArea.setRollingStep(GUISettings.explore_setting.scroll_step.value)
        self.explore_content_widget.runtimeUpdate()

    def resizeEvent(self, e):
        self.explore_content_widget.layoutPicBox(e.size(), e.oldSize())

    def mousePressEvent(self, e):
        pass
        # print(e.button())
        # if e.button() == Qt.MouseButton.ForwardButton and self.pre_button.isEnabled():
        #     self.nextPage()
        # elif e.button() == Qt.MouseButton.BackButton and self.next_button.isEnabled():
        #     self.prePage()


'''Explore widget end'''


def set_pixmap(pic_name):
    qimg = QImage(pic_name)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap

