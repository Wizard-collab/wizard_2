# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class confirm_widget(QtWidgets.QDialog):
    def __init__(self, message, title='Warning', reject_text='Cancel', accept_text='Continue', parent=None):
        super(confirm_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(title)

        self.security_sentence = None
        self.title = title
        self.message = message
        self.reject_text = reject_text
        self.accept_text = accept_text
        self.build_ui()
        self.connect_functions()

    def set_security_sentence(self, sentence):
        self.security_sentence = sentence
        self.security_widget.setVisible(1)
        self.security_sentence_label.setText(self.security_sentence)

    def set_important_message(self, message):
        self.important_message_label.setText(message)
        self.important_message_label.setVisible(1)

    def build_ui(self):
        self.setMinimumWidth(450)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.message_label = QtWidgets.QLabel(self.message)
        self.message_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.message_label)

        self.important_message_label = QtWidgets.QLabel()
        self.important_message_label.setObjectName('orange_label')
        self.important_message_label.setVisible(0)
        self.main_layout.addWidget(self.important_message_label)

        self.security_widget = QtWidgets.QWidget()
        self.security_layout = QtWidgets.QVBoxLayout()
        self.security_layout.setContentsMargins(0,0,0,0)
        self.security_layout.setSpacing(6)
        self.security_widget.setLayout(self.security_layout)
        self.main_layout.addWidget(self.security_widget)
        self.security_widget.setVisible(0)

        self.security_title = QtWidgets.QLabel('To confirm, please enter the following sentence')
        self.security_layout.addWidget(self.security_title)

        self.security_sentence_label = QtWidgets.QLabel()
        self.security_sentence_label.setObjectName('red_label')
        self.security_layout.addWidget(self.security_sentence_label)

        self.security_lineEdit = QtWidgets.QLineEdit()
        self.security_lineEdit.setStyleSheet('color:#f0605b;font:bold;')
        self.security_layout.addWidget(self.security_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.spaceItem = QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.buttons_layout.addSpacerItem(self.spaceItem)
        self.reject_button = QtWidgets.QPushButton(self.reject_text)
        self.reject_button.setDefault(False)
        self.reject_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.reject_button)
        self.accept_button = QtWidgets.QPushButton(self.accept_text)
        self.accept_button.setObjectName("red_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.accept_button)
        self.main_layout.addWidget(self.buttons_widget)

    def connect_functions(self):
        self.reject_button.clicked.connect(self.reject)
        self.accept_button.clicked.connect(self.confirm)

    def confirm(self):
        if self.security_sentence is None:
            self.accept()
        else:
            if self.security_lineEdit.text() == self.security_sentence:
                self.accept()
            else:
                logger.warning("The security sentence doesn't match")


