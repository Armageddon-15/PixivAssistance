from PyQt6.QtWidgets import QScrollArea
import PyQt6.QtGui as QtGui


class ScrollAreaWithStepSettings(QScrollArea):
    def __init__(self, widget):
        super(ScrollAreaWithStepSettings, self).__init__(widget)
        self.scroll_value = 0
        self.main = widget
        self.step = 1.0

    def setRollingStep(self, step: float):
        self.step = step

    def toTop(self):
        self.verticalScrollBar().setValue(0)
        self.scroll_value = 0

    def toBottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        self.scroll_value = self.verticalScrollBar().maximum()

    def toPosition(self, value: int):
        self.scroll_value = value
        self.scrollValueCheck()
        self.verticalScrollBar().setValue(self.scroll_value)

    def scrollValueCheck(self):
        self.scroll_value = max(0, self.scroll_value)
        self.scroll_value = min(self.scroll_value, self.verticalScrollBar().maximum())

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        self.scroll_value = self.verticalScrollBar().value()
        # print(self.verticalScrollBar().value())
        self.toPosition(self.scroll_value - e.angleDelta().y()/120 * self.step)
