# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
import webbrowser

# Wizard modules
from wizard.core import user
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class new_build_widget(QtWidgets.QWidget):
    def __init__(self, build, link, parent=None):
        super(new_build_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - New build !")

        self.build = build
        self.link = link

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def showEvent(self, event):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        if not screen:
            screen = QtWidgets.QApplication.desktop()
        screenRect = screen.availableGeometry()
        screen_maxX = screenRect.bottomRight().x()
        screen_maxY = screenRect.bottomRight().y()
        self.move(int((screenRect.x()+screen_maxX-self.width())/2), int((screenRect.y()+screen_maxY-self.height())/2))

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(20,20,20,20)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel("A new build is available !")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.build_label = QtWidgets.QLabel()
        self.build_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.build_label)

        self.download_button = QtWidgets.QPushButton('Download')
        self.download_button.setObjectName('blue_button')
        self.download_button.setIconSize(QtCore.QSize(20,20))
        self.download_button.setIcon(QtGui.QIcon(ressources._wizard_setup_icon_))
        self.main_layout.addWidget(self.download_button)

        self.link_label = QtWidgets.QLabel()
        self.link_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.link_label)

        self.ignore_layout = QtWidgets.QHBoxLayout()
        self.ignore_layout.setContentsMargins(0,0,0,0)
        self.ignore_layout.setSpacing(0)
        self.main_layout.addLayout(self.ignore_layout)

        self.ignore_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.ignore_checkbox = QtWidgets.QCheckBox('Ignore this alert')
        self.ignore_layout.addWidget(self.ignore_checkbox)

    def fill_ui(self):
        self.link_label.setText(self.link)
        self.build_label.setText(f"Build {self.build['MAJOR']}.{self.build['MINOR']}.{self.build['PATCH']}.{str(self.build['BUILDS']).zfill(4)}")
        self.ignore_checkbox.setChecked(not user.user().get_show_latest_build())

    def download(self):
        webbrowser.open_new_tab(self.link)

    def modify_ignore_latest_build(self):
        show_latest_build = not self.ignore_checkbox.isChecked()
        user.user().set_show_latest_build(show_latest_build)

    def connect_functions(self):
        self.download_button.clicked.connect(self.download)
        self.ignore_checkbox.stateChanged.connect(self.modify_ignore_latest_build)
