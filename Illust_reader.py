from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtWidgets import QVBoxLayout, QFileDialog
from PyQt6.QtCore import QRect, QMimeData

from Drag_and_Drop_Overlay import DnDWidget
import Parameters
import Illust
import sys
import os


class IllustReader(QWidget):
    def __init__(self, parent=None, illust: Illust.Illust = None):
        super(IllustReader, self).__init__(parent)
        self.illust = None
        self.setAcceptDrops(True)
        self.setMinimumSize(600, 350)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setRowCount(1)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().hide()

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.table)
        self.vbox.setSpacing(0)

        self.setIllust(illust)

        self.dnd_check = DnDWidget(self)
        self.dnd_check.setStyleSheet("color: rgba(0, 0, 0, 0);background-color: rgba(0, 0, 0, 120);")
        self.dnd_check.raise_()
        self.dnd_check.update.connect(self.printMimeData)
        self.dnd_check.setGeometry(QRect(0, 0, 0, 0))

    @staticmethod
    def readIllustData(illust: Illust.Illust):
        if illust is not None:
            illust.translateTagsToNone()
            return illust
        else:
            return None

    def setIllust(self, illust: Illust.Illust):
        self.illust = self.readIllustData(illust)
        if self.illust is not None:
            self.setLayoutData()

    def setLayoutData(self):
        data_dic = {"ID:": str(self.illust.id),
                    "Title:": self.illust.title,
                    "Type:": self.illust.type,
                    "Is Bookmarked:": str(self.illust.is_like),
                    "Page Count:": str(self.illust.page_count),
                    "Tags:": "",
                    "Description:": self.illust.description,
                    "Created Time:": self.illust.create_time.strftime("%Y年%m月%d日%H时%M分%S秒"),
                    "Is blocked:": str(self.illust.block),
                    "Author ID:": str(self.illust.user_id),
                    "Author Name:": self.illust.user_name,
                    "Downloaded Page(s):": "",
                    "Location:": self.illust.downloaded_path}

        # tags string
        tag_str = ""
        for i in range(len(self.illust.tags) - 1):
            if self.illust.translate_tags[i] is not None:
                tag_str += f"{self.illust.tags[i]}/({self.illust.translate_tags[i]}), "
            else:
                tag_str += f"{self.illust.tags[i]}, "
        tag_str = tag_str[:len(tag_str)-2]
        # downloaded page string
        page_str = ""
        for key in self.illust.downloaded:
            page_str += f"{key + 1}({self.illust.downloaded[key].name}), "
        page_str = page_str[:len(page_str)-2]

        data_dic["Tags:"] = tag_str
        data_dic["Downloaded Page(s):"] = page_str

        self.table.setRowCount(len(data_dic))

        i = 0
        for key in data_dic:
            key_item = QTableWidgetItem(key)
            data_item = QLabel(self)
            data_item.setWordWrap(True)
            data_item.setText(data_dic[key])

            self.table.setItem(i, 0, key_item)
            self.table.setCellWidget(i, 1, data_item)
            i += 1

    def printMimeData(self, data: QMimeData):
        file_path = data.text()
        file_path = file_path.replace(r"file:///", "")
        if os.path.isfile(file_path):
            extension = os.path.splitext(file_path)[1]
            if extension == Parameters.data_extension:
                self.setIllust(Illust.loadIllustDataByPath(file_path))

    def dragEnterEvent(self, e) -> None:
        self.dnd_check.setGeometry(0, 0, self.size().width(), self.size().height())


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Illust Reader")

        self.illust_reader_widget = IllustReader(parent=self)
        self.load_btn = QPushButton(self)
        self.load_btn.setText("Load")
        self.load_btn.clicked.connect(self.clickLoadBtn)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.illust_reader_widget)
        self.vbox.addWidget(self.load_btn)

    def clickLoadBtn(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilters([f"Illust Data (*{Parameters.data_extension})", "All(*)"])
        dialog.setDirectory(os.path.abspath(Parameters.illust_data_path))
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            self.illust_reader_widget.setIllust(Illust.loadIllustDataByPath(file_path))


if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    window.show()
    sys.exit(app.exec())
