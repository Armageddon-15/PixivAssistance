from Parameters import *
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QComboBox
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtCore import Qt
import Illust
import sys
import os


class APP(QWidget):
    def __init__(self):
        super(APP, self).__init__()
        self.setWindowTitle("Open Folders")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.domain_combo = QComboBox(self)
        self.main_combo = QComboBox(self)
        self.sp_combo = QComboBox(self)

        self.set_domain_combox()
        self.set_main_combox()
        self.set_sp_comobx()

        self.btn = QPushButton(self)
        self.btn.setText("Open")
        self.btn.clicked.connect(self.btn_click)

        self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.domain_combo)
        self.hbox.addWidget(self.main_combo)
        self.hbox.addWidget(self.sp_combo)
        self.hbox.addWidget(self.btn)

    def set_domain_combox(self):
        self.domain_combo.addItem("Main", download_path)
        self.domain_combo.addItem("GIF", gif_path)
        self.domain_combo.addItem("Group", group_path)

    def set_main_combox(self):
        self.main_combo.addItem("SFW", "")
        self.main_combo.addItem("NSFW", "R-18\\")

    def set_sp_comobx(self):
        self.sp_combo.addItem("Main", "")
        _, sp_tags = Illust.getSpecialTags()
        for tag in sp_tags:
            self.sp_combo.addItem(tag, tag)

    def btn_click(self):
        rel_path = self.domain_combo.currentData() + self.main_combo.currentData() + self.sp_combo.currentData()
        os.startfile(rel_path)
        print(rel_path)


app = QApplication([])
window = APP()
window.show()
sys.exit(app.exec())
