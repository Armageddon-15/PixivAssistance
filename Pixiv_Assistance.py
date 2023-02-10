from PyQt6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtWidgets import QSizePolicy, QStackedWidget, QSizeGrip, QApplication
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QImage, QPixmap, QBrush, QPainter, QPen
from PyQt6.QtCore import Qt, QSize, QRect, QPoint
from Explore_Widget import ExploreWidget
from Detail_Widget import DetailWin
from PA_Setting_GUI import PASettingWidget

import Illust
import os
import cv2
import sys
import GUISettings

APP_NAME = "Pixiv Assistance"
VERSION = 'Version: 0.2.1'


# resizable frameless widget
class SideGrip(QWidget):
    def __init__(self, parent, edge):
        QWidget.__init__(self, parent)
        if edge == Qt.Edge.LeftEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.Edge.TopEdge:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.Edge.RightEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mouse_pos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(int(geo.right() - width))
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(int(geo.bottom() - height))
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(int(width), int(window.height()))

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(int(window.width()), int(height))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            delta = event.position() - self.mouse_pos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None


# movable title bar
class MoveLabel(QLabel):
    def __init__(self, parent):
        super(MoveLabel, self).__init__()
        self.parent = parent
        self.start = QPoint(0, 0)
        self.ismax = False

    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.position())

    def mouseMoveEvent(self, event):
        self.parent.showNormal()
        self.ismax = False
        end = self.mapToGlobal(event.position())
        movement = QPoint(int(end.x() - self.start.x()), int(end.y() - self.start.y()))
        # print("x = %d, y = %d" % (self.mapToGlobal(movement).x(), self.mapToGlobal(movement).y()))
        self.parent.setGeometry(self.parent.mapToGlobal(movement).x(),
                                self.parent.mapToGlobal(movement).y(),
                                self.parent.width(),
                                self.parent.height())
        self.start = end

    def mouseDoubleClickEvent(self, e):
        if self.ismax:
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
        self.ismax = not self.ismax


class HeadLabel(QLabel):
    def __init__(self, parent):
        super(HeadLabel, self).__init__(parent)
        self.main = parent
        self.head_size = None
        self.runtimeUpdate()
        self.setScaledContents(True)

    def setHeadLabel(self):
        pixmap_img = getCirclePixmap(GUISettings.main_setting.head_icon_path.value, self.head_size)
        self.setPixmap(pixmap_img)

    def mouseReleaseEvent(self, e) -> None:
        global_pos_TL = self.mapToGlobal(QPoint(0, 0))
        global_pos_BR = self.mapToGlobal(QPoint(self.size().width(), self.size().height()))
        cursor_pos = e.globalPosition().toPoint()

        if e.button() == Qt.MouseButton.LeftButton:
            if global_pos_TL.x() < cursor_pos.x() < global_pos_BR.x() and global_pos_TL.y() < cursor_pos.y() < global_pos_BR.y():
                self.main.showSettingWidget()

    def runtimeUpdate(self):
        self.head_size = GUISettings.main_setting.head_icon_size.value
        self.setMinimumSize(QSize(self.head_size, self.head_size))
        self.setMaximumSize(QSize(self.head_size, self.head_size))
        self.setHeadLabel()


# main widget
class Window(QWidget):
    _gripSize = GUISettings.main_setting.grip_size.value

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setStyleSheet("background-color : rgb(208, 205, 210);")
        self.setWindowSize()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setting_widget = PASettingWidget(self)

        # set top frame
        self.top_frame = QFrame()
        self.top_frame.setFrameShape(QFrame.Shape.NoFrame)

        # set left frame in top frame
        self.top_left_frame = QFrame(self.top_frame)
        self.top_left_frame.setFrameShape(QFrame.Shape.NoFrame)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.top_left_frame.setSizePolicy(sizePolicy)

        # set head pic in top left frame
        self.head_label = HeadLabel(self)

        #    layout the head pic
        self.tl_frame_vbox = QVBoxLayout(self.top_left_frame)
        self.tl_frame_vbox.setContentsMargins(0, 0, 0, 0)
        self.tl_frame_vbox.addWidget(self.head_label)
        self.top_left_frame.setLayout(self.tl_frame_vbox)

        # set middle frame in top frame
        self.top_mid_frame = QFrame(self.top_frame)
        self.top_mid_frame.setFrameShape(QFrame.Shape.NoFrame)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        self.top_mid_frame.setSizePolicy(sizePolicy)

        # set the name of this gui
        self.main_name_label = MoveLabel(self)
        self.main_name_label.setText(APP_NAME)
        self.main_name_label.setStyleSheet(f"font: 700 {GUISettings.main_setting.title_font_size.value}pt \"Microsoft PhagsPa\";color:rgb(30, 30, 30) ")
        self.main_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # set seprate frame
        self.top_mid_sperate_frame = QFrame(self.top_mid_frame)
        self.top_mid_sperate_frame.setFrameShape(QFrame.Shape.HLine)
        # gradient = QGradient()
        # gradient.setColorAt(0, 0)
        # gradient.setColorAt(0.5, 255)
        # gradient.setColorAt(1, 0)
        self.top_mid_sperate_frame.palette().setColor(QPalette.ColorRole.ToolTipText, QColor(25, 25, 25))

        # set name of illust
        self.illust_name_label = QLabel(self.top_mid_frame)
        self.illust_name_label.setOpenExternalLinks(True)
        self.illust_name_label.setStyleSheet(f"font: 500 {GUISettings.main_setting.illust_title_font_size.value}pt \"Microsoft YaHei UI\";color:rgb(80, 80, 80) ")
        self.illust_name_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        #    layout things in middle frame
        self.tm_frame_vbox = QVBoxLayout(self.top_mid_frame)
        self.tm_frame_vbox.setContentsMargins(0, 0, 0, 0)
        self.tm_frame_vbox.setSpacing(0)
        self.tm_frame_vbox.addWidget(self.main_name_label)
        self.tm_frame_vbox.addWidget(self.top_mid_sperate_frame)
        self.tm_frame_vbox.addWidget(self.illust_name_label)

        # set right frame of top frame
        self.top_right_frame = QFrame(self.top_frame)
        self.top_right_frame.setFrameShape(QFrame.Shape.NoFrame)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.top_right_frame.setSizePolicy(sizePolicy)

        # set min button
        self.min_label = QPushButton(self.top_right_frame)
        self.min_label.clicked.connect(self.btnMinClicked)
        operate_btn_size = GUISettings.main_setting.operate_btn_size.value
        self.min_label.setMaximumSize(QSize(operate_btn_size, operate_btn_size))
        # self.min_label.setText('-')
        self.min_label.setIcon(QIcon('icons\\minimize.png'))
        self.min_label.setFlat(True)  # change in future...
        # set max button
        self.max_label = QPushButton(self.top_right_frame)
        self.max_label.clicked.connect(self.btnMaxClicked)
        self.max_label.setMaximumSize(QSize(32, 32))
        # self.max_label.setText('+')
        self.max_label.setIcon(QIcon('icons\\maxmize.png'))
        self.max_label.setFlat(True)  # change in future...
        # set close button
        self.close_label = QPushButton(self.top_right_frame)
        self.close_label.clicked.connect(self.btnCloseClicked)
        self.close_label.setMaximumSize(QSize(32, 32))
        # self.close_label.setText('X')
        self.close_label.setIcon(QIcon('icons\\close.png'))
        self.close_label.setFlat(True)  # change in future...
        # layout icon in right frame
        self.tr_frame_hbox = QHBoxLayout(self.top_right_frame)
        self.tr_frame_hbox.setContentsMargins(0, 0, 0, 0)
        self.tr_frame_hbox.setSpacing(5)
        self.tr_frame_hbox.addWidget(self.min_label)
        self.tr_frame_hbox.addWidget(self.max_label)
        self.tr_frame_hbox.addWidget(self.close_label)

        # layout frames in top frame
        self.top_frame_hbox = QHBoxLayout(self.top_frame)
        self.top_frame_hbox.setContentsMargins(0, 0, 0, 0)
        self.top_frame_hbox.setSpacing(0)
        self.top_frame_hbox.addWidget(self.top_left_frame, 0, Qt.AlignmentFlag.AlignLeft)
        self.top_frame_hbox.addWidget(self.top_mid_frame)
        self.top_frame_hbox.addWidget(self.top_right_frame, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # set middle frame
        self.mid_frame = QFrame()
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.mid_frame.setSizePolicy(sizePolicy)
        self.mid_frame.setFrameShape(QFrame.Shape.NoFrame)

        # set right of middle frame
        self.stackedWidget = QStackedWidget(self.mid_frame)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)

        # create explore widget in stacked widget
        self.explore_widget = QWidget(self.stackedWidget)
        self.explore_win = ExploreWidget(self)
        self.exp_widget_vbox = QVBoxLayout(self.explore_widget)
        self.exp_widget_vbox.addWidget(self.explore_win)

        # create detail widget in stacked widget
        self.detail_widget = QWidget(self.stackedWidget)
        self.detail_win = DetailWin(self)
        self.detail_vbox = QVBoxLayout(self.detail_widget)
        self.detail_vbox.addWidget(self.detail_win)

        # setup stacked widget
        self.stackedWidget.addWidget(self.explore_widget)
        self.stackedWidget.addWidget(self.detail_widget)

        # layout middle frame
        self.mid_hbox = QHBoxLayout(self.mid_frame)
        self.mid_hbox.setContentsMargins(0, 0, 0, 0)
        self.mid_hbox.setSpacing(2)
        self.mid_hbox.addWidget(self.stackedWidget)

        # set bottom frame
        self.bottom_frame = QFrame()
        self.bottom_frame.setFrameShape(QFrame.Shape.NoFrame)

        # set things in bottom frame
        self.version_label = QLabel(self.bottom_frame)
        self.version_label.setText(VERSION)
        #    set middle of bottom frame
        self.btm_mid_frame = QFrame()
        #    set right of bottom frame
        self.btm_right_frame = QFrame(self.bottom_frame)
        self.btm_right_frame.setFrameShape(QFrame.Shape.NoFrame)

        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.version_label.setSizePolicy(sizePolicy)
        sizePolicy.setHorizontalStretch(8)
        self.btm_mid_frame.setSizePolicy(sizePolicy)
        sizePolicy.setHorizontalStretch(3)
        self.btm_right_frame.setSizePolicy(sizePolicy)

        #    set things in bottom right frame
        self.state_label = QLabel(self.btm_right_frame)
        self.state_label.setText("Download State:")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
        self.download_count = 0
        self.total_download_count = 0
        self.download_count_label = QLabel(self.btm_right_frame)
        self.download_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_count_label.setText(f"{self.download_count}/{self.total_download_count}")
        #    layout things in bottom right frame
        self.br_frame_hbox = QHBoxLayout(self.btm_right_frame)
        self.br_frame_hbox.addWidget(self.state_label)
        self.br_frame_hbox.addWidget(self.download_count_label)
        #    end set

        # layout bottom frame
        self.bottom_frame_hbox = QHBoxLayout(self.bottom_frame)
        self.bottom_frame_hbox.setContentsMargins(0, 0, 0, 0)
        self.bottom_frame_hbox.addWidget(self.version_label)
        self.bottom_frame_hbox.addWidget(self.btm_mid_frame)
        self.bottom_frame_hbox.addWidget(self.btm_right_frame)

        # set layout of three main frame
        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.addWidget(self.top_frame, 0, Qt.AlignmentFlag.AlignTop)
        self.vbox.addWidget(self.mid_frame)
        self.vbox.addWidget(self.bottom_frame, 0, Qt.AlignmentFlag.AlignBottom)

        # setup resize grip
        self.sideGrips = [
            SideGrip(self, Qt.Edge.LeftEdge),
            SideGrip(self, Qt.Edge.TopEdge),
            SideGrip(self, Qt.Edge.RightEdge),
            SideGrip(self, Qt.Edge.BottomEdge),
        ]
        # corner grips should be "on top" of everything, otherwise the side grips
        # will take precedence on mouse events, so we are adding them *after*;
        # alternatively, widget.raise_() can be used
        self.cornerGrips = [QSizeGrip(self) for i in range(4)]
        for cg in self.cornerGrips:
            cg.raise_()

        self.setLayout(self.vbox)

    def btnCloseClicked(self):
        self.saveGeoPosition()
        self.close()

    def btnMaxClicked(self):
        self.showMaximized()
        self.max_label.setIcon(QIcon('icons\\normal.png'))
        self.max_label.clicked.connect(self.btnMaxToNormalClicked)

    def btnMinClicked(self):
        self.showMinimized()

    def btnMaxToNormalClicked(self):
        self.showNormal()
        self.max_label.setIcon(QIcon('icons\\maxmize.png'))
        self.max_label.clicked.connect(self.btnMaxClicked)
        self.explore_win.update()

    def setDownloadState(self, downloading=0, total=0):
        self.download_count += downloading
        self.total_download_count += total
        self.download_count_label.setText(f'{self.download_count}/{self.total_download_count}')

    def setWindowSize(self):
        if GUISettings.win_setting.use_this.getValue():
            widget_width = GUISettings.win_setting.width.value
            widget_height = GUISettings.win_setting.height.value
            widget_x = GUISettings.win_setting.x.value
            widget_y = GUISettings.win_setting.y.value
        else:
            size = getScreenSize()
            widget_width = int(size.width() * 0.495)
            widget_height = int(size.height() * 0.98)
            widget_x = int(size.width() * 0.0025)
            widget_y = int(size.height() * 0.01)

        self.setGeometry(widget_x, widget_y, widget_width, widget_height)

    def saveGeoPosition(self):
        geo = self.geometry()
        GUISettings.win_setting.setGeo(geo.x(), geo.y(), geo.width(), geo.height())
        GUISettings.saveAndLoad()

    def showSettingWidget(self):
        self.setting_widget.show()

    def toDetailPage(self, illust, index):
        url = '''<a href="https://www.pixiv.net/artworks/%d">%s</a>''' % (illust.id, illust.title)
        self.illust_name_label.setText(url)
        print("get ", illust.id)
        self.detail_win.loadLarge(illust, index)
        self.detail_win.jumpToTop()
        self.stackedWidget.setCurrentIndex(1)
        # self.detail_win.rematch()

    def preIllust(self, index):
        index = index - 1
        if index < 0:
            print("It's the first illust!")
        else:
            illust = self.explore_win.explore_content_widget.illust_list[index]
            self.toDetailPage(illust, index)

    def nextIllust(self, index):
        index = index + 1
        try:
            illust = self.explore_win.explore_content_widget.illust_list[index]
        except IndexError:
            print("It's the last illust!")
        else:
            self.toDetailPage(illust, index)

    def toExplorePage(self):
        self.illust_name_label.setText("")
        self.stackedWidget.setCurrentIndex(0)

    def runtimeUpdate(self):
        self.head_label.runtimeUpdate()
        self.explore_win.runtimeUpdate()
        self.detail_win.runtimeUpdate()
        self.main_name_label.setStyleSheet(f"font: 700 {GUISettings.main_setting.title_font_size.value}pt \"Microsoft PhagsPa\";color:rgb(30, 30, 30) ")
        self.illust_name_label.setStyleSheet(f"font: 500 {GUISettings.main_setting.illust_title_font_size.value}pt \"Microsoft YaHei UI\";color:rgb(80, 80, 80) ")
        operate_btn_size = GUISettings.main_setting.operate_btn_size.value
        self.min_label.setMaximumSize(QSize(operate_btn_size, operate_btn_size))
        self.max_label.setMaximumSize(QSize(operate_btn_size, operate_btn_size))
        self.close_label.setMaximumSize(QSize(operate_btn_size, operate_btn_size))


    @property
    def gripSize(self):
        return self._gripSize

    def setGripSize(self, size):
        if size == self._gripSize:
            return
        self._gripSize = max(2, size)
        self.updateGrips()

    def updateGrips(self):
        self.setContentsMargins(*[self.gripSize] * 4)

        outRect = self.rect()
        # an "inner" rect used for reference to set the geometries of size grips
        inRect = outRect.adjusted(self.gripSize, self.gripSize, -self.gripSize, -self.gripSize)

        # top left
        self.cornerGrips[0].setGeometry(
            QRect(outRect.topLeft(), inRect.topLeft()))
        # top right
        self.cornerGrips[1].setGeometry(
            QRect(outRect.topRight(), inRect.topRight()).normalized())
        # bottom right
        self.cornerGrips[2].setGeometry(
            QRect(inRect.bottomRight(), outRect.bottomRight()))
        # bottom left
        self.cornerGrips[3].setGeometry(
            QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized())

        # left edge
        self.sideGrips[0].setGeometry(
            0, inRect.top(), self.gripSize, inRect.height())
        # top edge
        self.sideGrips[1].setGeometry(
            inRect.left(), 0, inRect.width(), self.gripSize)
        # right edge
        self.sideGrips[2].setGeometry(
            inRect.left() + inRect.width(),
            inRect.top(), self.gripSize, inRect.height())
        # bottom edge
        self.sideGrips[3].setGeometry(
            self.gripSize, inRect.top() + inRect.height(),
            inRect.width(), self.gripSize)

    def resizeEvent(self, event):
        self.updateGrips()


def getCirclePixmap(pic_name, size, line_width=1):
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
        painter2.drawEllipse(int(line_width/2), int(line_width/2), size - line_width, size - line_width)
    return img


def getScreenSize():
    height = QApplication.primaryScreen().size().height()
    width = QApplication.primaryScreen().size().width()
    size = QSize(width, height)
    return size


def main():
    Illust.login()
    Illust.createAcquiredPaths()
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
