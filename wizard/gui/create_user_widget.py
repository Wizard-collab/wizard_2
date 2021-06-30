# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import logging_widget
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import site
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class create_user_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(create_user_widget, self).__init__(parent)
        self.image_file = None
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel("Sign up")
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.credentials_label = QtWidgets.QLabel("Credentials")
        self.main_layout.addWidget(self.credentials_label)

        self.user_name_lineEdit = QtWidgets.QLineEdit()
        self.user_name_lineEdit.setPlaceholderText('User name')
        self.main_layout.addWidget(self.user_name_lineEdit)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.password_confirm_lineEdit = gui_utils.password_lineEdit()
        self.password_confirm_lineEdit.setPlaceholderText('Confirm Password')
        self.main_layout.addWidget(self.password_confirm_lineEdit)

        self.email_lineEdit = QtWidgets.QLineEdit()
        self.email_lineEdit.setPlaceholderText('User Email')
        self.main_layout.addWidget(self.email_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100,20,QtWidgets.QSizePolicy.Fixed,
                                                    QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.credentials_label = QtWidgets.QLabel("Profile picture")
        self.main_layout.addWidget(self.credentials_label)

        self.profile_picture_button = QtWidgets.QPushButton()
        self.profile_picture_button.setFixedSize(60,60)
        self.profile_picture_button.setIcon(QtGui.QIcon(ressources._default_profile_))
        self.profile_picture_button.setIconSize(QtCore.QSize(54,54))
        self.main_layout.addWidget(self.profile_picture_button)

        self.spaceItem = QtWidgets.QSpacerItem(100,20,QtWidgets.QSizePolicy.Fixed,
                                                    QtWidgets.QSizePolicy.Fixed)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.admin_label = QtWidgets.QLabel("The section below is optional")
        self.main_layout.addWidget(self.admin_label)

        self.admin_password_lineEdit = gui_utils.password_lineEdit()
        self.admin_password_lineEdit.setPlaceholderText('Administrator Password')
        self.main_layout.addWidget(self.admin_password_lineEdit)


        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.buttons_layout.addWidget(self.quit_button)
        self.sign_up_button = QtWidgets.QPushButton('Sign up')
        self.sign_up_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.sign_up_button)

        self.logging_widget = logging_widget.logging_widget(self)
        self.main_layout.addWidget(self.logging_widget)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_up_button.clicked.connect(self.apply)
        self.profile_picture_button.clicked.connect(self.update_profile_picture)

    def apply(self):
        user_name = self.user_name_lineEdit.text()
        password = self.password_lineEdit.text()
        confirm_password = self.password_confirm_lineEdit.text()
        email = self.email_lineEdit.text()
        admin_password = self.admin_password_lineEdit.text()
        if confirm_password == password:
            if site.create_user(user_name,
                                    password,
                                    email,
                                    admin_password,
                                    self.image_file):
                self.accept()
        else:
            logger.warning("User passwords doesn't matches")

    def update_profile_picture(self):
        options = QtWidgets.QFileDialog.Options()
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                            "All Files (*);;Images Files (*.png);;Images Files (*.jpg);;Images Files (*.jpeg)",
                            options=options)
        if image_file:
            extension = image_file.split('.')[-1].upper()
            if (extension == 'PNG') or (extension == 'JPG') or (extension == 'JPEG'):
                self.image_file = image_file
                self.profile_picture_button.setIcon(QtGui.QIcon(image_file))
            else:
                logger.warning('{} is not a valid image file...'.format(image_file))

