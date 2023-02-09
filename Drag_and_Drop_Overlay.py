from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QMimeData, Qt
from PyQt6 import QtCore


class DnDWidget(QLabel):
    update = QtCore.pyqtSignal(QMimeData)

    def __init__(self, parent):
        super().__init__(parent)
        self.data = None
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

    def dragEnterEvent(self, e) -> None:
        e.acceptProposedAction()

    def dropEvent(self, e) -> None:
        self.data = e.mimeData()
        self.update.emit(self.data)
        # print(self.data.text())
        self.setGeometry(0, 0, 0, 0)

    def dragLeaveEvent(self, e) -> None:
        self.data = None

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.MiddleButton:
            self.setGeometry(0, 0, 0, 0)

    def enterEvent(self, e) -> None:
        self.setGeometry(0, 0, 0, 0)
