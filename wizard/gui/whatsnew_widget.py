# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import yaml
import logging

# Wizard modules
from wizard.vars import ressources
from wizard.core import application
from wizard.core import user

logger = logging.getLogger(__name__)

class whatsnew_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(whatsnew_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - What's new ?")

        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def build_ui(self):
        self.resize(600,600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('header_frame')
        self.header_widget.setStyleSheet('#header_frame{background-color:rgba(119, 133, 222, 190);}')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(20,20,20,20)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.icon_image = QtWidgets.QLabel()
        self.icon_image.setPixmap(QtGui.QIcon(ressources._whatsnew_icon_).pixmap(60))
        self.header_layout.addWidget(self.icon_image)

        self.title_label = QtWidgets.QLabel("What's new ?")
        self.title_label.setObjectName('title_label')
        self.header_layout.addWidget(self.title_label)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.version_label = QtWidgets.QLabel()
        self.version_label.setObjectName('bold_label')
        self.header_layout.addWidget(self.version_label)

        self.textedit_layout = QtWidgets.QHBoxLayout()
        self.textedit_layout.setContentsMargins(10,10,10,10)
        self.textedit = QtWidgets.QTextEdit()
        self.textedit.setObjectName('transparent_widget')
        self.textedit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.textedit_layout.addWidget(self.textedit)
        self.main_layout.addLayout(self.textedit_layout)

        self.footer_widget = QtWidgets.QWidget()
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(20,20,20,20)
        self.footer_widget.setLayout(self.footer_layout)
        self.main_layout.addWidget(self.footer_widget)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.show_at_startup_checkbox = QtWidgets.QCheckBox('Show at startup')
        self.footer_layout.addWidget(self.show_at_startup_checkbox)

    def fill_ui(self):
        self.show_at_startup_checkbox.setChecked(user.user().get_show_whatsnew())

        version_dic = application.get_version()
        self.version_label.setText(f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']} - build {version_dic['builds']}")

        with open(ressources._whatsnew_html_, 'r') as f:
            html_data = f.read()

        self.textedit.insertHtml(html_data)

    def connect_functions(self):
        self.show_at_startup_checkbox.stateChanged.connect(self.toggle_show_at_startup)

    def toggle_show_at_startup(self, state):
        user.user().set_show_whatsnew(state)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
