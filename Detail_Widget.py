from PyQt6.QtWidgets import QLabel, QPushButton, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QImage, QPixmap, QBrush, QPainter, QPen, QMovie
from PyQt6.QtCore import Qt, QSize, QRect, QPoint, QThread
from PyQt6 import QtCore
from ScrollAreaWithStepSettings import ScrollAreaWithStepSettings
from PAEnum import *
import Parameters
import GUISettings

import Illust
import os
import cv2


class DownloadDetailThread(QThread):
    over = QtCore.pyqtSignal(int, str)

    def __init__(self, illust: Illust.Illust = None, index=None, add_func=None):
        super().__init__()
        self.illust = illust
        self.index = index
        self.add_func = add_func

    def run(self):
        self.over.emit(self.index, "Downloading")
        state = self.illust.saveByIndex(self.index - 1)
        if state[self.index - 1] == DownloadState.successful:
            self.over.emit(self.index, "Successful")
            self.add_func(1, 0)
        print("download No.%d picture" % self.index)


class DownloadLargeThread(QThread):
    over = QtCore.pyqtSignal(int, str)

    def __init__(self, illust: Illust.Illust, index: int):
        super().__init__()
        self.illust = illust
        self.index = index
        self.saving_path = ""
        self.state = DownloadState.hint

    def run(self) -> None:
        self.saving_path, self.state = self.illust.saveLargeByIndex(self.index)
        # print("downloaded", self.index, self.saving_path)
        self.over.emit(self.index, self.saving_path)


'''Detail Widget'''


class HoverWidget(QWidget):
    def __init__(self, widget):
        super(HoverWidget, self).__init__(widget)
        self.main = widget
        self.ratio = 0.1
        self.ll = 0
        self.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.raise_()

        self.move_button = QPushButton(self)
        self.move_button.setStyleSheet("border: none;color: rgba(255, 255, 255, 0);")
        self.move_button.setFont(QFont("Microsoft JhengHei", 100, 0, False))

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.move_button)
        self.setLayout(self.vbox)

    def setParameters(self, ratio, ll):
        self.ratio = ratio
        self.ll = ll
        if self.ll == 0:
            self.left()
        else:
            self.right()

    def left(self):
        self.move_button.setText("◀")
        self.move_button.clicked.connect(self.preIllust)

    def right(self):
        self.move_button.setText("▶")
        self.move_button.clicked.connect(self.nextIllust)

    def rematch(self):
        if self.ll == 0:
            self.setGeometry(0, 0, int(self.main.width() * self.ratio), self.main.height())
        else:
            self.setGeometry(int(self.main.width() * (1 - self.ratio)) - 20, 0,
                             int(self.main.width() * self.ratio), self.main.height())
        self.move_button.setFixedSize(int(self.main.width() * self.ratio), int(self.main.width() * self.ratio))
        self.move_button.setFont(QFont("Microsoft JhengHei", int(self.main.width() * self.ratio/1.5), 0, False))

        # print(self.pos())

    def preIllust(self):
        self.main.preIllust()

    def nextIllust(self):
        self.main.nextIllust()

    def enterEvent(self, e):
        pass
        self.setStyleSheet('background-color: rgba(0, 0, 0, 80);')
        self.move_button.setStyleSheet("border: none;color: rgba(255, 255, 255, 255);")

    def leaveEvent(self, e):
        pass
        self.setStyleSheet('background-color: rgba(0, 0, 0, 0);')
        self.move_button.setStyleSheet("border: none;color: rgba(255, 255, 255, 0);")


class TagLabel(QWidget):
    def __init__(self, parent):
        super(TagLabel, self).__init__(parent=parent)
        self.sharp = QLabel(self)
        self.sharp.setText("#")
        self.sharp.setFont(QFont("Microsoft YaHei UI", GUISettings.detail_setting.tag_sharp_size.value, 0, False))
        self.sharp.setStyleSheet("color:rgb(102, 176, 255);")
        self.tag_name = QLabel(self)
        font = QFont("Microsoft Sans Serif", GUISettings.detail_setting.tag_font_size.value, 0, False)
        font.setBold(True)
        self.tag_name.setFont(font)
        self.tag_name.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tag_tlname = QLabel(self)
        self.tag_tlname.setFont(QFont("Microsoft JhengHei UI Light", GUISettings.detail_setting.translate_tag_font_size.value, 0, False))
        self.tag_tlname.setStyleSheet("color:rgb(100, 100, 100);")
        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.sharp)
        self.hbox.addWidget(self.tag_name, 1, Qt.AlignmentFlag.AlignLeft)
        self.hbox.addWidget(self.tag_tlname, 2, Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.hbox)

    def initTagColor(self):
        if self.tag_name.text() == "R-18" or self.tag_name.text() == "R-18G":
            self.tag_name.setStyleSheet("color:rgb(255, 39, 43);")
            self.sharp.setStyleSheet("color:rgba(255, 39, 43, 0);")
        elif self.tag_name.text() == "AI生成":
            self.sharp.setStyleSheet("color:rgba(255, 39, 43, 0);")
        else:
            self.tag_name.setStyleSheet("color:rgb(29, 114, 194);")

    def enterEvent(self, e) -> None:
        if self.tag_name.text() != "R-18" and self.tag_name.text() != "R-18G":
            self.tag_name.setStyleSheet("color:rgb(125, 171, 225);")

    def leaveEvent(self, e) -> None:
        if self.tag_name.text() != "R-18" and self.tag_name.text() != "R-18G":
            self.tag_name.setStyleSheet("color:rgb(29, 114, 194);")
        elif self.tag_name.text() == "AI生成":
            self.sharp.setStyleSheet("color:rgba(255, 39, 43, 0);")

    def mouseReleaseEvent(self, e) -> None:
        global_pos_TL = self.mapToGlobal(QPoint(0, 0))
        global_pos_BR = self.mapToGlobal(QPoint(self.size().width(), self.size().height()))
        cursor_pos = e.globalPosition().toPoint()

        if e.button() == Qt.MouseButton.LeftButton:
            if global_pos_TL.x() < cursor_pos.x() < global_pos_BR.x() and global_pos_TL.y() < cursor_pos.y() < global_pos_BR.y():
                Illust.searchTagPage(self.tag_name.text())


class DetailLabel(QLabel):
    def __init__(self, widget):
        super(DetailLabel, self).__init__(parent=widget)
        self.main = widget
        self.illust = None
        self.gif = False
        self.index = 0
        self.download_text = ""

        self.dl_btn = QPushButton(self)
        self.dl_btn.setText("↓")
        self.dl_btn.raise_()
        self.dl_btn.raise_()
        self.dl_btn.setFlat(True)
        self.dl_btn.setFont(QFont("Microsoft JhengHei", 25, 0, False))
        self.dl_btn.clicked.connect(self.btnDlClicked)

        self.index_text = QLabel(self)
        font = QFont("Microsoft JhengHei", 20, 0, False)
        font.setBold(True)
        self.index_text.setFont(font)
        self.index_text.setGeometry(5, 0, 100, 40)
        self.index_text.setStyleSheet("color : rgb(20, 20, 20); background-color : rgba(0, 0, 0, 0)")

        self.setScaledContents(True)
        self.btn2_constrain = QRect(self.size().width() - GUISettings.detail_setting.btn_size - 3,
                                    self.size().height() - GUISettings.detail_setting.btn_size - 3,
                                    GUISettings.detail_setting.btn_size, GUISettings.detail_setting.btn_size)
        self.dl_btn.setGeometry(self.btn2_constrain)
        self.download_worker = DownloadDetailThread()

        self.download_state_label = QLabel(self)
        self.download_state_label.setStyleSheet("color : rgb(200, 200, 200); background-color : rgba(0, 0, 0, 0)")
        self.download_state_label.setFont(QFont("Microsoft JhengHei", 15, 0, False))
        self.download_state_label.raise_()
        self.download_state_label.setText("")

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.download_state_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

    def rematch(self):
        try:
            if self.gif:
                # print("Detail gif rematch")
                ratio = self.movie().currentImage().size().height() / self.movie().currentImage().size().width()
                self_width = self.movie().currentImage().size().width()
            else:
                # print("Detail rematch")
                ratio = self.pixmap().size().height() / self.pixmap().size().width()
                self_width = self.pixmap().size().width()
        except ZeroDivisionError:
            self.deleteLater()
            return 0
        width = max(int(self.main.size().width() * 0.4),
                    min(int(self.main.size().height() / ratio * 0.75),
                        self_width * 3, int(self.main.size().width() * 7 / 10)))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaximumSize(width, int(width * ratio))
        self.setMinimumSize(width, int(width * ratio))

        self.index_text.setText(str(self.index))
        btn_pos_width = self.size().width() - GUISettings.detail_setting.btn_size - 3
        btn_pos_height = self.size().height() - GUISettings.detail_setting.btn_size - 3
        # print(btn_pos_width, btn_pos_height, self.size())
        self.btn2_constrain = QRect(btn_pos_width, btn_pos_height, GUISettings.detail_setting.btn_size, GUISettings.detail_setting.btn_size)
        self.dl_btn.setGeometry(self.btn2_constrain)

    def setDownloadState(self, index, string):
        self.download_text = string
        self.download_state_label.setText(string)

    def btnDlClicked(self):
        self.main.setDownloadState(0, 1)
        self.download_worker = DownloadDetailThread(self.illust, self.index, self.main.setDownloadState)
        self.download_worker.start()
        self.download_worker.over.connect(self.setDownloadState)

    def runtimeUpdate(self):
        pass

    def mouseDoubleClickEvent(self, e):
        self.btnDlClicked()

    def resizeEvent(self, e) -> None:
        self.rematch()


class AuthWidget(QWidget):
    def __init__(self):
        super(AuthWidget, self).__init__()
        # self.setStyleSheet("background-color: rgb(200, 200, 200);")

        self.top_frame = QFrame(self)
        self.auth_head = QLabel(self.top_frame)
        self.auth_head.setPixmap(setCirclePixmap("icons\\07.jpg", GUISettings.detail_setting.author_head_icon_size.value, 1))
        self.auth_name = QLabel(self.top_frame)
        self.auth_name.setText("_")
        font = QFont("Microsoft JhengHei", GUISettings.detail_setting.author_name_font_size.value, 0, False)
        font.setBold(True)
        self.auth_name.setFont(font)

        self.top_frame_hbox = QHBoxLayout(self.top_frame)
        self.top_frame_hbox.addWidget(self.auth_head)
        self.top_frame_hbox.addWidget(self.auth_name, 1, Qt.AlignmentFlag.AlignLeft)

        self.tags_frame = QFrame(self)
        self.tags_gbox = QGridLayout(self.tags_frame)
        self.tags_gbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tags_gbox.setSpacing(GUISettings.detail_setting.tag_spacing.value)
        self.tags = []

        self.create_time = QLabel()
        self.create_time.setFont(QFont("等线", GUISettings.detail_setting.time_font_size.value, 0, False))

        self.description = QLabel(self)
        self.description.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.description.setFont(QFont("黑体", GUISettings.detail_setting.description_font_size.value, 0, False))
        self.description.setStyleSheet("word-wrap: break-word;")
        self.description.setWordWrap(True)
        self.description.setOpenExternalLinks(True)
        self.description.setTextFormat(Qt.TextFormat.RichText)
        self.description.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(30, 0, 0, 0)
        self.vbox.addWidget(self.top_frame)
        self.vbox.addWidget(self.tags_frame, 1, Qt.AlignmentFlag.AlignTop)
        self.vbox.addWidget(self.create_time, 0, Qt.AlignmentFlag.AlignTop)
        self.vbox.addWidget(self.description, 0, Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.vbox)

    def showLarge(self, illust: Illust.Illust):
        if illust is not None:
            head_path = Parameters.auth_head_path + str(illust.user_id) + os.path.splitext(illust.user_head)[1]
            self.auth_head.setPixmap(setCirclePixmap(head_path, GUISettings.detail_setting.author_head_icon_size.value, 1))
            self.auth_name.setText(illust.user_name)
            self.description.setText(illust.description)
            self.create_time.setText(illust.create_time.strftime("%Y年%m月%d日%H时%M分%S秒 创建"))
            while self.tags_gbox.count():
                self.tags_gbox.takeAt(0).widget().deleteLater()
            i = 0
            illust.translateTagsToNone()
            for num in range(len(illust.tags)):
                r = int(i / GUISettings.detail_setting.tags_per_line)
                tag = TagLabel(self)
                tag.tag_name.setText(illust.tags[num])
                tag.tag_tlname.setText(illust.translate_tags[num])
                tag.initTagColor()
                self.tags_gbox.addWidget(tag, r, i % GUISettings.detail_setting.tags_per_line, 1, 1)
                self.tags.append(tag)
                i = i + 1

    def runtimeUpdate(self, illust: Illust.Illust):
        self.showLarge(illust)
        self.tags_gbox.setSpacing(GUISettings.detail_setting.tag_spacing.value)
        self.create_time.setFont(QFont("等线", GUISettings.detail_setting.time_font_size.value, 0, False))
        self.description.setFont(QFont("黑体", GUISettings.detail_setting.description_font_size.value, 0, False))
        font = QFont("Microsoft JhengHei", GUISettings.detail_setting.author_name_font_size.value, 0, False)
        font.setBold(True)
        self.auth_name.setFont(font)


class DetailWin(QWidget):
    def __init__(self, widget):
        super(DetailWin, self).__init__(widget)
        self.main = widget
        self.scroll_value = 0
        self.illust = None
        self.load_time = 0
        self.index = 0

        self.scrollpage = ScrollAreaWithStepSettings(self)
        self.scrollpage.setWidgetResizable(True)
        self.scrollpage.setFrameShape(QFrame.Shape.NoFrame)

        self.detail_content_widget = QWidget(self.scrollpage)
        # set things in left frame
        self.pre_illust = HoverWidget(self)
        self.pre_illust.setParameters(0.1, 0)
        self.next_illust = HoverWidget(self)
        self.next_illust.setParameters(0.1, 1)
        self.left_frame = QFrame(self.detail_content_widget)

        # self.left_frame.setStyleSheet("background-color: rgb(200, 200, 200);")
        self.ec_vbox = QVBoxLayout(self.left_frame)
        self.ec_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ec_vbox.setSpacing(5)
        self.ec_vbox.setContentsMargins(0, 0, 0, 0)
        self.pic_stream = []

        # set things in right widget
        self.right_widget = AuthWidget()

        # layout frames
        self.hbox = QHBoxLayout(self.detail_content_widget)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.setSpacing(0)
        self.hbox.addWidget(self.left_frame)
        self.hbox.addWidget(self.right_widget, 0, Qt.AlignmentFlag.AlignTop)

        # layout scroll page
        self.ex_hbox = QHBoxLayout(self.scrollpage)
        self.ex_hbox.addWidget(self.detail_content_widget)
        self.ex_hbox.setContentsMargins(0, 0, 0, 0)
        self.ex_hbox.setSpacing(0)
        self.scrollpage.setWidget(self.detail_content_widget)
        self.scrollpage.setRollingStep(GUISettings.detail_setting.scroll_step.value)
        self.scrollpage.setStyleSheet(open("ScrollBar.qss").read())

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.scrollpage)
        self.vbox.setSpacing(0)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)

        # return button
        self.return_btn = QPushButton(self)
        self.return_btn.clicked.connect(self.btnReturnClicked)
        self.return_btn.raise_()
        self.return_btn.setText("◀")
        self.return_btn.setFont(QFont("Microsoft JhengHei", 25, 0, False))

        # load new button
        self.load_new_btn = QPushButton(self)
        self.load_new_btn.clicked.connect(self.btnLoadNewClicked)
        self.load_new_btn.setText("N")
        font = QFont("Microsoft JhengHei", 30, 0, False)
        font.setBold(True)
        self.load_new_btn.setFont(font)

        # download large thread
        self.download_large_thread = []

    def loadLarge(self, illust: Illust.Illust, illust_index):
        self.load_time = 0
        self.pic_stream.clear()
        self.illust = illust
        self.index = illust_index
        if self.illust.page_count <= GUISettings.detail_setting.stream_per_load:
            self.load_new_btn.setDisabled(True)
        else:
            self.load_new_btn.setDisabled(False)
        self.load_time = min(max(0, illust.page_count), GUISettings.detail_setting.stream_per_load.value)
        self.showLarge(0, self.load_time)

        for thread_index in range(self.load_time):
            thread = DownloadLargeThread(illust, thread_index)
            thread.over.connect(self.assignDetailLabel)
            thread.start()
            self.download_large_thread.append(thread)

    def showLarge(self, start, end):
        if start == 0:
            while self.ec_vbox.count():
                self.ec_vbox.takeAt(0).widget().deleteLater()

        for index in range(start, end):
            # print(index)
            detail_pic = DetailLabel(self)
            detail_pic.illust = self.illust
            detail_pic.setPixmap(setPixmap("icons/downloading.png"))
            detail_pic.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            detail_pic.index = index + 1
            self.ec_vbox.addWidget(detail_pic, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            self.pic_stream.append(detail_pic)
        # print(type(self.ec_vbox.itemAt(0).widget()))
        self.right_widget.showLarge(self.illust)
        # self.rematch()

    def assignDetailLabel(self, detail_index, path):
        # print(self.geometry())
        detail_pic = self.pic_stream[detail_index]
        if self.illust.type == "ugoira":
            detail_pic.gif = True
            gif = QMovie(path)
            detail_pic.setMovie(gif)
            gif.start()
        else:
            detail_pic.setPixmap(setPixmap(path))
        detail_pic.rematch()
        # self.pic_stream[detail_index] = detail_pic

    def jumpToTop(self):
        self.scrollpage.toTop()

    def rematch(self):
        # print(self.geometry())
        self.left_frame.setMinimumSize(int(self.size().width() * 0.7), 0)
        for pic in self.pic_stream:
            pic.rematch()
        btn_size = GUISettings.detail_setting.btn_size.value
        self.return_btn.setGeometry(self.size().width() - btn_size*2, self.size().height() - 60, btn_size, btn_size)
        self.load_new_btn.setGeometry(self.size().width() - (btn_size*3+10), self.size().height() - 60, btn_size, btn_size)
        self.pre_illust.rematch()
        self.next_illust.rematch()

    def btnReturnClicked(self):
        self.main.toExplorePage()

    def btnLoadNewClicked(self):
        self.download_large_thread = []
        end = min(self.illust.page_count, self.load_time + GUISettings.detail_setting.stream_per_load)
        self.showLarge(self.load_time, end)

        for thread_index in range(self.load_time, end):
            thread = DownloadLargeThread(self.illust, thread_index)
            thread.over.connect(self.assignDetailLabel)
            self.download_large_thread.append(thread)
            thread.start()

        self.load_time = end
        if self.load_time >= self.illust.page_count:
            self.load_new_btn.setDisabled(True)
        self.rematch()

    def preIllust(self):
        self.main.preIllust(self.index)

    def nextIllust(self):
        self.main.nextIllust(self.index)

    def setDownloadState(self, downloaded=0, total=0):
        self.main.setDownloadState(downloaded, total)

    def runtimeUpdate(self):
        for detail_pic in self.pic_stream:
            detail_pic.runtimeUpdate()
        self.scrollpage.setRollingStep(GUISettings.detail_setting.scroll_step.value)
        self.right_widget.runtimeUpdate(self.illust)
        self.rematch()

    def resizeEvent(self, e):
        self.rematch()

    def wheelEvent(self, e) -> None:
        self.scrollpage.wheelEvent(e)


'''Detail widget end'''


def setPixmap(pic_name):
    qimg = QImage(pic_name)
    pixmap = QPixmap.fromImage(qimg)
    return pixmap


def setCirclePixmap(pic_name, size, line_width=1):
    if os.path.splitext(pic_name)[1] == ".gif":
        cap = cv2.VideoCapture(pic_name)
        ret, img = cap.read()
    else:
        img = cv2.imread(pic_name)
    img = cv2.resize(img, (size, size), cv2.INTER_NEAREST)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    w, h, c = img.shape
    img[:, :, 3] = 255
    qimg = QImage(img.data, w, h, c * w, QImage.Format.Format_RGBA8888)
    qimg = circleQimage(qimg, size, line_width)
    pixmap = QPixmap.fromImage(qimg)
    pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    pixmap_img = QPixmap(pixmap)
    return pixmap_img


def circleQimage(qimage, size, line_width=0):
    img = QImage(size, size, QImage.Format.Format_RGBA8888)
    img.fill(Qt.GlobalColor.transparent)
    brush = QBrush(qimage)
    painter = QPainter(img)
    painter.setBrush(brush)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()
    if line_width != 0:
        painter2 = QPainter(img)
        painter2.setPen(QPen(Qt.GlobalColor.gray, line_width, style=Qt.PenStyle.SolidLine))
        painter2.drawEllipse(int(line_width / 2), int(line_width / 2), size - line_width, size - line_width)
    return img


def getScreenSize():
    height = QApplication.primaryScreen().size().height()
    width = QApplication.primaryScreen().size().width()
    size = QSize(width, height)
    return size
