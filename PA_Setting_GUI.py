from PyQt6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QCheckBox, QSpinBox
from PyQt6.QtWidgets import QSizePolicy, QApplication, QLineEdit, QFileDialog, QAbstractSpinBox

import sys
import GUISettings
import Parameters
import os


class SettingModify:
    def __init__(self, setting: GUISettings.SettingValue = None, **kwargs):
        self.is_setting_none = True
        if setting is not None:
            self.is_setting_none = False
        self.setting = setting

    def getValue(self):
        pass

    def setValue(self, v):
        pass

    def applyToSetting(self):
        if not self.is_setting_none:
            self.setting.setValue(self.getValue())

    def updateSetting(self):
        self.setValue(self.setting.getValue())


class PACheckBoxSetting(QFrame, SettingModify):
    def __init__(self, parent=None, name="Check Box", check=False, setting: GUISettings.SettingValue = None):
        super(PACheckBoxSetting, self).__init__(parent=parent, setting=setting)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

        self.check_box = QCheckBox(self)
        self.check_box.setText(name)
        # self.check_box.setStyleSheet("QCheckBox::indicator {border: 1px solid black; border-radius: 3px; }")

        if not self.is_setting_none:
            self.setValue(self.setting.getValue())
        else:
            self.setValue(check)

        self.stretch_frame = QFrame(self)
        self.hbox = QHBoxLayout(self)
        margins = 5
        self.hbox.setContentsMargins(15, margins, margins, margins)
        self.hbox.addWidget(self.check_box)
        self.hbox.addWidget(self.stretch_frame)

    def getValue(self):
        return self.check_box.isChecked()

    def setValue(self, check: bool):
        self.check_box.setChecked(check)


class PASpinBoxSetting(QFrame, SettingModify):
    def __init__(self, parent=None, name="Spin Box", value=0, max_value=999, min_va=0, setting: GUISettings.SettingValue = None):
        super(PASpinBoxSetting, self).__init__(parent=parent, setting=setting)
        self.name_label = QLabel(self)
        self.name_label.setText(name)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.name_label.setSizePolicy(sizePolicy)

        self.spinbox = QSpinBox(self)
        self.setMaxValue(max_value)
        self.setMinValue(min_va)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.spinbox.setSizePolicy(sizePolicy)
        self.spinbox.setStyleSheet(open("SpinBox.qss").read())
        self.spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        if not self.is_setting_none:
            self.updateSetting()
        else:
            self.setValue(value)

        self.stretch_frame = QFrame(self)

        self.hbox = QHBoxLayout(self)
        margins = 5
        self.hbox.setContentsMargins(15, margins, margins, margins)
        self.hbox.addWidget(self.name_label)
        self.hbox.addWidget(self.stretch_frame)
        self.hbox.addWidget(self.spinbox)

    def getValue(self):
        return self.spinbox.value()

    def setValue(self, v: int):
        self.spinbox.setValue(v)

    def setMaxValue(self, v: int):
        self.spinbox.setMaximum(v)

    def setMinValue(self, v: int):
        self.spinbox.setMinimum(v)


class PAFileSetting(QFrame, SettingModify):
    def __init__(self, parent=None, name="path", setting: GUISettings.SettingValue = None):
        super(PAFileSetting, self).__init__(parent=parent, setting=setting)
        self.name_label = QLabel(self)
        self.name_label.setText(name)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.name_label.setSizePolicy(sizePolicy)

        self.path_line = QLineEdit(self)
        self.path_line.setMinimumSize(250, 0)
        self.path_line.setStyleSheet("border-radius: 2px;border: 1px solid black;")

        if not self.is_setting_none:
            self.updateSetting()
        else:
            self.setValue("")

        self.read_file_btn = QPushButton(self)
        self.read_file_btn.setText("...")
        self.read_file_btn.setMinimumSize(25, 0)
        self.read_file_btn.setStyleSheet("border-radius: 2px;border: 1px solid black;")
        self.read_file_btn.clicked.connect(self.btnClicked)

        self.stretch_frame = QFrame(self)
        self.hbox = QHBoxLayout(self)
        margins = 5
        self.hbox.setContentsMargins(15, margins, margins, margins)
        self.hbox.addWidget(self.name_label)
        self.hbox.addWidget(self.stretch_frame)
        self.hbox.addWidget(self.path_line)
        self.hbox.addWidget(self.read_file_btn)

    def btnClicked(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilters([f"Picture file (*.png  *.jpg)", "All(*)"])
        dialog.setDirectory(os.path.abspath(Parameters.icon_path))
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            try:
                file_path = os.path.relpath(file_path)
            except ValueError:
                pass
            self.setValue(file_path)

    def getValue(self):
        return self.path_line.text()

    def setValue(self, s: str):
        self.path_line.setText(s)


class PASettingClassFrame(QFrame):
    def __init__(self, parent=None, name="Settings"):
        super(PASettingClassFrame, self).__init__(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)

        self.name_label = QLabel(self)
        self.name_label.setText(name)

        self.vbox = QVBoxLayout(self)
        self.vbox.setSpacing(0)
        self.vbox.addWidget(self.name_label)

        self.setting_frames = []

    def layoutSettingFrames(self):
        for setting_frame in self.setting_frames:
            self.vbox.addWidget(setting_frame)

    def addSettingFrame(self, setting_frame):
        self.setting_frames.append(setting_frame)
        self.vbox.addWidget(setting_frame)

    def applyToSettings(self):
        for setting_frame in self.setting_frames:
            setting_frame.applyToSetting()

    def updateSettings(self):
        for setting_frame in self.setting_frames:
            setting_frame.updateSetting()

    def length(self):
        return len(self.setting_frames)


class PASettingFrame(QFrame):
    def __init__(self, parent=None):
        super(PASettingFrame, self).__init__(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.setting_classes = []
        self.stretch_frame = QFrame(self)
        # self.stretch_frame.setStyleSheet("background-color: rgb(0, 255, 255);")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.stretch_frame.setSizePolicy(sizePolicy)
        self.vboxs = []
        self.hbox = QHBoxLayout(self)
        self.setSettings()

    def setSettings(self):
        res_setting_class = PASettingClassFrame(self, "Resolution Setting:")
        res_setting_class.addSettingFrame(PACheckBoxSetting(self, "Remember last closed size", setting=GUISettings.win_setting.use_this))
        self.setting_classes.append(res_setting_class)

        main_win_setting_class = PASettingClassFrame(self, "Main Window Settings:")
        main_win_setting_class.addSettingFrame(PASpinBoxSetting(self, "Head icon size:", setting=GUISettings.main_setting.head_icon_size))
        main_win_setting_class.addSettingFrame(PAFileSetting(self, "Head path:", setting=GUISettings.main_setting.head_icon_path))
        # main_win_setting_class.addSettingFrame(PASpinBoxSetting(self, "Grip size:", setting=GUISettings.main_setting.grip_size))
        main_win_setting_class.addSettingFrame(PASpinBoxSetting(self, "Title font Size:", setting=GUISettings.main_setting.title_font_size))
        main_win_setting_class.addSettingFrame(PASpinBoxSetting(self, "Illust title font Size:", setting=GUISettings.main_setting.illust_title_font_size))
        main_win_setting_class.addSettingFrame(PASpinBoxSetting(self, "Operate button Size:", setting=GUISettings.main_setting.operate_btn_size))
        self.setting_classes.append(main_win_setting_class)

        exp_setting_class = PASettingClassFrame(self, "Explore Settings:")
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Illust title font size:", setting=GUISettings.explore_setting.illust_title_font_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Count font size:", setting=GUISettings.explore_setting.count_font_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "AI font size:", setting=GUISettings.explore_setting.ai_font_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Download state font size:", setting=GUISettings.explore_setting.state_font_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Like button size:", setting=GUISettings.explore_setting.btn_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "GIF icon size:", setting=GUISettings.explore_setting.gif_icon_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Thumbnail size:", setting=GUISettings.explore_setting.thumbnail_size))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Thumbnail spacing:", setting=GUISettings.explore_setting.thumbnail_spacing))

        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Scroll step:", setting=GUISettings.explore_setting.scroll_step))
        exp_setting_class.addSettingFrame(PASpinBoxSetting(self, "Illust per page", setting=GUISettings.explore_setting.pic_per_page))
        self.setting_classes.append(exp_setting_class)

        detail_setting_class = PASettingClassFrame(self, "Detail Settings:")
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Button size:", setting=GUISettings.detail_setting.btn_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Author head size:", setting=GUISettings.detail_setting.author_head_icon_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Author name font size:", setting=GUISettings.detail_setting.author_name_font_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Tag font size:", setting=GUISettings.detail_setting.tag_font_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Translate tag font size:", setting=GUISettings.detail_setting.translate_tag_font_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Tag sharp size:", setting=GUISettings.detail_setting.tag_sharp_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Tags per line:", min_va=1, setting=GUISettings.detail_setting.tags_per_line))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Tag spacing:", setting=GUISettings.detail_setting.tag_spacing))

        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Time font size:", setting=GUISettings.detail_setting.time_font_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Description font size:", setting=GUISettings.detail_setting.description_font_size))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Download pictures each load:", setting=GUISettings.detail_setting.stream_per_load))
        detail_setting_class.addSettingFrame(PASpinBoxSetting(self, "Scroll step:", setting=GUISettings.detail_setting.scroll_step))

        self.setting_classes.append(detail_setting_class)

        self.layoutSettings()

    def layoutSettings(self):
        i = 0
        vbox = QVBoxLayout()
        for s_class in self.setting_classes:
            if i % 2 == 0 or s_class.length() >= 10:
                vbox = QVBoxLayout()
                self.vboxs.append(vbox)
            else:
                i += 1
            s_class.layoutSettingFrames()
            vbox.addWidget(s_class)
            i += 1

        for box in self.vboxs:
            box.addWidget(QFrame(self))
            self.hbox.addLayout(box)

        self.hbox.addWidget(self.stretch_frame)

    def applyAllSettings(self):
        for s_class in self.setting_classes:
            s_class.applyToSettings()

    def updateAllSettings(self):
        for s_class in self.setting_classes:
            s_class.updateSettings()


class PASettingWidget(QWidget):
    def __init__(self, window=None):
        super(PASettingWidget, self).__init__()
        self.main = window
        self.setting_frame = PASettingFrame(self)
        self.btn_frame = QFrame(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.btn_frame.setSizePolicy(sizePolicy)
        self.stretch_frame = QFrame(self.btn_frame)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        self.stretch_frame.setSizePolicy(sizePolicy)
        self.apply_btn = QPushButton(self.btn_frame)
        self.apply_btn.setText("Apply")
        self.apply_btn.clicked.connect(self.applyBtnClicked)

        self.accept_btn = QPushButton(self.btn_frame)
        self.accept_btn.setText("Accept")
        self.accept_btn.clicked.connect(self.acceptBtnClicked)

        self.cancel_btn = QPushButton(self.btn_frame)
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.clicked.connect(self.cancelBtnClicked)

        self.btn_hbox = QHBoxLayout(self.btn_frame)
        self.btn_hbox.addWidget(self.stretch_frame)
        self.btn_hbox.addWidget(self.apply_btn)
        self.btn_hbox.addWidget(self.accept_btn)
        self.btn_hbox.addWidget(self.cancel_btn)

        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.setting_frame)
        self.vbox.addWidget(self.btn_frame)

    def applyBtnClicked(self):
        self.setting_frame.applyAllSettings()
        GUISettings.saveAndLoad()
        self.setting_frame.updateAllSettings()
        if self.main is not None:
            self.main.runtimeUpdate()

    def acceptBtnClicked(self):
        self.applyBtnClicked()
        self.close()

    def cancelBtnClicked(self):
        self.close()


def main():
    app = QApplication([])
    window = PASettingWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
