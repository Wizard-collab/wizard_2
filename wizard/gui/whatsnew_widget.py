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

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_widget.setObjectName('transparent_widget')
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setContentsMargins(20,20,20,20)
        self.scrollArea_layout.setSpacing(0)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(4)
        self.content_widget.setLayout(self.content_layout)
        self.scrollArea_layout.addWidget(self.content_widget)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)
        self.main_layout.addWidget(self.scrollArea)

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

        with open('ressources/whatsnew.yaml', 'r') as f:
            whatsnew_dic = yaml.load(f, Loader=yaml.Loader)

        for title in whatsnew_dic.keys():
            type = whatsnew_dic[title]['type']
            comment = whatsnew_dic[title]['comment']
            widget = row_widget(title, type, comment)
            self.content_layout.addWidget(widget)

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

class row_widget(QtWidgets.QFrame):
    def __init__(self, title, type, comment, parent=None):
        super(row_widget, self).__init__(parent)
        self.title = title
        self.type = type
        self.comment = comment
        self.build_ui()

    def build_ui(self):
        self.setObjectName('round_frame')
        self.setStyleSheet('#round_frame{background-color:rgba(255,255,255,10)}')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(10,10,10,10)
        self.main_layout.setSpacing(10)
        self.setLayout(self.main_layout)

        self.tag_widget = QtWidgets.QWidget()
        self.tag_widget.setObjectName('transparent_widget')
        self.tag_layout = QtWidgets.QVBoxLayout()
        self.tag_widget.setFixedWidth(10)
        self.tag_layout.setContentsMargins(0,3,0,0)
        self.tag_layout.setSpacing(3)
        self.tag_widget.setLayout(self.tag_layout)
        self.main_layout.addWidget(self.tag_widget)

        self.tag = QtWidgets.QFrame()
        self.tag.setFixedSize(10,10)
        self.tag_layout.addWidget(self.tag)

        if self.type == 'debug':
            color = '#ff5d5d'
        elif self.type == 'modification':
            color = '#ffad4d'
        elif self.type == 'new':
            color = '#95d859'
        self.tag.setStyleSheet(f'background-color:{color}; border-radius:5px;')

        self.tag_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('transparent_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(3)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.title_label = QtWidgets.QLabel(f"{self.type} - {self.title}")
        self.title_label.setObjectName('title_label_2')
        self.title_label.setWordWrap(True)
        self.content_layout.addWidget(self.title_label)

        if self.comment:
            self.comment_label = QtWidgets.QLabel(self.comment)
            self.comment_label.setObjectName('gray_label')
            self.comment_label.setWordWrap(True)
            self.content_layout.addWidget(self.comment_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

