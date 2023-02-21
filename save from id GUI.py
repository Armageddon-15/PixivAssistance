from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFrame, QScrollArea
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QCheckBox
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRect, QThread, QRegularExpression, QMimeData
from PyQt6 import QtCore
import Parameters
from typing import Union
from Drag_and_Drop_Overlay import DnDWidget
import sys
import Illust
import re
import os


def saveFromId(id: int, index: Union[list, int] = 0):
    if type(index) is list:
        print("length of list is %d" % len(index))
    elif index > 0:
        print("1 picture")
    else:
        print("all pictures")

    try:
        illust = Illust.getIllustByID(id)
    except Exception as e:
        print(e)
        return False
    else:
        print(illust)
        try:
            illust.saveAll(index)
        except ValueError as e:
            print(e)
            return False

        except IndexError as e:
            print(e)
            return False
        else:
            if not os.path.exists(Parameters.illust_thbnl_path + illust.thumbnail_name):
                print("illust thb not exist")
                illust.noNeedThumbnail()
            return True


def strToList(string: str) -> list:
    """
    string example : "1 53 9 9-1 5"
    the returned list is sequential, so 9-1 will convert to reversed(range(1, 9+1))
    but if string contain 0, it will return 0, which means save all
    """
    sp_list = Illust.removeObjInList(string.split(" "), "")

    saved_pages = []
    for pages in sp_list:
        if pages.find("-") != -1:
            s_e = pages.split("-")
            s_e[0] = int(s_e[0])
            s_e[1] = int(s_e[1])
            if s_e[0] > s_e[1]:
                saved_pages.extend(reversed(range(s_e[1], s_e[0]+1)))
            elif s_e[0] < s_e[1]:
                saved_pages.extend(range(s_e[0], s_e[1] + 1))
            else:
                saved_pages.append(s_e[0])
        else:
            saved_pages.append(int(pages))

    pages_dict = {}

    for page in saved_pages:
        if page == 0:
            return [0]
        index = saved_pages.index(page)
        pages_dict.update({page: index})

    return list(pages_dict.keys())


class SaveFromIDDownloader(QThread):
    update = QtCore.pyqtSignal(bool)

    def __init__(self, id, index):
        super(SaveFromIDDownloader, self).__init__()
        self.id = id
        self.index = index

    def run(self) -> None:
        # print(self.id)
        # print(type(self.index), self.index)
        check = saveFromId(self.id, self.index)
        self.update.emit(check)
        print("\nDone!\n")


class SaveFromID(QWidget):
    over = QtCore.pyqtSignal(int)

    def __init__(self, main, index):
        super(SaveFromID, self).__init__(main)
        self.main = main
        self.index = index
        self.hover = False

        self.setMinimumSize(550, 0)
        self.setMaximumSize(550, 160)
        self.setAcceptDrops(True)

        self.id_input_frame = QFrame(self)
        self.id_input_line = QLineEdit(self.id_input_frame)
        self.id_input_line.setPlaceholderText("ONLY numbers")
        self.id_input_line.dragEnabled()

        int_validator = QRegularExpressionValidator()
        q_re = QRegularExpression()
        q_re.setPattern(R'\d*')
        int_validator.setRegularExpression(q_re)
        self.id_input_line.setValidator(int_validator)
        self.id_input_text = QLabel(self.id_input_frame)
        self.id_input_text.setText("Illust ID:")
        self.id_clear_btn = QPushButton(self.id_input_frame)
        self.id_clear_btn.setText("Clear")
        self.id_clear_btn.clicked.connect(self.ClearIdInput)

        self.id_input_hbox = QHBoxLayout(self.id_input_frame)
        self.id_input_hbox.addWidget(self.id_input_text)
        self.id_input_hbox.addWidget(self.id_input_line)
        self.id_input_hbox.addWidget(self.id_clear_btn)
        self.id_input_hbox.setContentsMargins(5, 0, 5, 0)

        self.page_input_frame = QFrame(self)
        self.page_input_line = QLineEdit(self.page_input_frame)
        self.page_input_line.setPlaceholderText("ONLY numbers, space and dash, default is 0, means save all")
        self.page_input_line.setValidator(QRegularExpressionValidator(QRegularExpression(R'(\d{1,3}[ -])*')))
        self.page_input_text = QLabel(self.page_input_frame)
        self.page_input_text.setText("Pages:")
        self.page_clear_btn = QPushButton(self.page_input_frame)
        self.page_clear_btn.setText("Clear")
        self.page_clear_btn.clicked.connect(self.ClearPageInput)

        self.page_input_hbox = QHBoxLayout(self.page_input_frame)
        self.page_input_hbox.addWidget(self.page_input_text)
        self.page_input_hbox.addWidget(self.page_input_line)
        self.page_input_hbox.addWidget(self.page_clear_btn)
        self.page_input_hbox.setContentsMargins(5, 0, 5, 0)

        self.operate_frame = QFrame()
        self.add_space_btn = QPushButton(self.operate_frame)
        self.add_space_btn.setText("Space( )")
        self.add_space_btn.clicked.connect(self.addSpaceBtn)
        self.add_dash_btn = QPushButton(self.operate_frame)
        self.add_dash_btn.setText("Dash(-)")
        self.add_dash_btn.clicked.connect(self.addDashBtn)
        self.operate_hbox = QHBoxLayout(self.operate_frame)
        self.operate_hbox.addWidget(self.add_space_btn)
        self.operate_hbox.addWidget(self.add_dash_btn)
        self.operate_hbox.setContentsMargins(5, 2, 5, 0)

        self.btn_frame = QFrame(self)
        self.single_dl_check = QCheckBox(self.btn_frame)
        self.single_dl_check.setText("Create folder while saving single picture in a group-type illust")
        self.btn = QPushButton(self.btn_frame)
        self.btn.setText("Save")
        self.btn.clicked.connect(self.btnStart)

        self.btn_frame_hbox = QHBoxLayout(self.btn_frame)
        self.btn_frame_hbox.addWidget(self.single_dl_check)
        self.btn_frame_hbox.addWidget(self.btn)
        self.btn_frame_hbox.setContentsMargins(5, 2, 5, 2)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.id_input_frame)
        self.vbox.addWidget(self.page_input_frame)
        self.vbox.addWidget(self.operate_frame)
        self.vbox.addWidget(self.btn_frame)
        self.vbox.setContentsMargins(5, 0, 5, 0)

        self.dnd_check = DnDWidget(self)
        self.dnd_check.setStyleSheet("color: rgba(0, 0, 0, 0);background-color: rgba(0, 0, 0, 120);")
        self.dnd_check.raise_()
        self.dnd_check.update.connect(self.setIdInput)
        self.dnd_check.setGeometry(QRect(0, 0, 0, 0))
        self.saving_thread = QThread()

    def ClearIdInput(self):
        self.id_input_line.clear()

    def ClearPageInput(self):
        self.page_input_line.clear()

    def setIdInput(self, data: QMimeData):
        text = data.text()
        if text.find("file:///") != -1 and text.find("illust_") != -1:
            match_text = os.path.basename(text).split("_")[1]
            print(match_text)
            self.id_input_line.setText(match_text)
        else:
            match_texts = re.findall(r'[0-9]+', text)
            if len(match_texts) > 0:
                match_text = match_texts[len(match_texts)-1]
                self.id_input_line.setText(match_text)

    def addStringToPageLine(self, s: str, pos: int):
        text = self.page_input_line.text()
        text = text[:pos] + s + text[pos:]
        self.page_input_line.setText(text)
        self.page_input_line.setFocus()
        self.page_input_line.setCursorPosition(pos+1)

    def addSpaceBtn(self):
        self.addStringToPageLine(" ", self.page_input_line.cursorPosition())

    def addDashBtn(self):
        self.addStringToPageLine("-", self.page_input_line.cursorPosition())

    def btnStart(self):
        self.btn.setDisabled(True)
        saving_list = strToList(self.page_input_line.text())
        self.saving_thread.quit()
        if self.id_input_line.text() != "":
            if self.page_input_line.text() == "":
                self.saving_thread = SaveFromIDDownloader(int(self.id_input_line.text()), 0)
            else:
                if self.single_dl_check.checkState() == Qt.CheckState.Checked:
                    # print(self.single_dl_check.checkState())
                    self.saving_thread = SaveFromIDDownloader(int(self.id_input_line.text()), saving_list)
                else:
                    # print(len(saving_list))
                    if len(saving_list) == 1 and type(saving_list) is list:
                        self.saving_thread = SaveFromIDDownloader(int(self.id_input_line.text()), saving_list[0])
                    else:
                        self.saving_thread = SaveFromIDDownloader(int(self.id_input_line.text()), saving_list)
            self.saving_thread.start()
            self.saving_thread.update.connect(self.DestroyWhenDone)

        else:
            print("nothing input")
            self.btn.setDisabled(False)

    def DestroyWhenDone(self, is_done):
        if is_done:
            self.over.emit(self.index)
            self.deleteLater()
        else:
            self.btn.setDisabled(False)

    def keyPressEvent(self, event) -> None:
        if event.key() != 0:
            if event.key() == 16777220 or event.key() == 16777221:
                # those two int is value of main enter and pad enter
                if self.hover:
                    pass
                    print(self.hover, self.index)
                    self.btnStart()

    def enterEvent(self, e) -> None:
        self.hover = True

    def leaveEvent(self, e) -> None:
        self.hover = False

    def dragEnterEvent(self, e) -> None:
        self.dnd_check.setGeometry(0, 0, 550, 160)

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.RightButton:
            self.DestroyWhenDone(True)


class GroupSaveGUI(QWidget):
    def __init__(self):
        super(GroupSaveGUI, self).__init__()

        self.setWindowTitle("Save Illust From ID")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAcceptDrops(True)

        self.setMinimumSize(600, 600)
        self.setMaximumSize(600, 9999)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(0)

        self.top_frame = QWidget(self.scroll_area)
        self.ex_hbox = QHBoxLayout(self.scroll_area)
        self.ex_hbox.addWidget(self.top_frame)
        self.ex_hbox.setContentsMargins(0, 0, 0, 0)
        self.ex_hbox.setSpacing(0)

        self.scroll_area.setWidget(self.top_frame)

        self.btn = QPushButton(self)
        self.btn.setText("Add")
        self.btn.clicked.connect(self.addModule)

        self.modules = []

        module = SaveFromID(self, 0)
        module.over.connect(self.deleteModule)
        self.modules.append(module)

        self.top_frame_vobx = QVBoxLayout(self.top_frame)
        self.top_frame_vobx.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.top_frame_vobx.addWidget(module)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.scroll_area)
        self.vbox.addWidget(self.btn)

    def addModule(self):
        module = SaveFromID(self, len(self.modules))
        module.over.connect(self.deleteModule)
        self.modules.append(module)
        self.top_frame_vobx.addWidget(module)
        # self.printModulesLength()
        return module

    def deleteModule(self, index):
        self.modules.pop(index)
        # print("Module %d is deleted" % index)
        self.updateModules()

    def updateModules(self):
        i = 0
        for module in self.modules:
            module.index = i
            i += 1

    def printModulesLength(self):
        print("Modules length is %d" % len(self.modules))

    def dragEnterEvent(self, e) -> None:
        e.acceptProposedAction()

    def dropEvent(self, e) -> None:
        data = e.mimeData()
        module = self.addModule()
        module.setIdInput(data)


def main():
    Illust.login()
    Illust.createAcquiredPaths()
    app = QApplication([])
    window = GroupSaveGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
