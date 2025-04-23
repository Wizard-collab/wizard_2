# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import image
from wizard.core import repository
from wizard.vars import ressources

logger = logging.getLogger(__name__)


class create_user_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(create_user_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create user")

        self.image_file = None
        self.use_image_file = 0
        self.build_ui()
        self.connect_functions()
        self.get_random_profile_picture()

    def build_ui(self):
        self.setMinimumWidth(350)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.spaceItem = QtWidgets.QSpacerItem(100, 12, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.title_label = QtWidgets.QLabel("Create user")
        self.title_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(
            0, 12, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
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

        self.spaceItem = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Policy.Fixed,
                                               QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.credentials_label = QtWidgets.QLabel("Profile picture")
        self.main_layout.addWidget(self.credentials_label)

        self.profile_picture_button = QtWidgets.QPushButton()
        self.profile_picture_button.setFixedSize(60, 60)
        self.profile_picture_button.setStyleSheet('border-radius:30px;')
        self.profile_picture_button.setIconSize(QtCore.QSize(54, 54))
        self.main_layout.addWidget(self.profile_picture_button)

        self.spaceItem = QtWidgets.QSpacerItem(100, 25, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.championship_label = QtWidgets.QLabel("Championship")
        self.main_layout.addWidget(self.championship_label)

        self.championship_participation = QtWidgets.QCheckBox(
            'Championship participation')
        self.championship_participation.setObjectName('android_checkbox')
        self.main_layout.addWidget(self.championship_participation)

        self.spaceItem = QtWidgets.QSpacerItem(100, 20, QtWidgets.QSizePolicy.Policy.Fixed,
                                               QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.admin_label = QtWidgets.QLabel("The section below is optional")
        self.main_layout.addWidget(self.admin_label)

        self.admin_password_lineEdit = gui_utils.password_lineEdit()
        self.admin_password_lineEdit.setPlaceholderText(
            'Administrator Password')
        self.main_layout.addWidget(self.admin_password_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100, 25, QtWidgets.QSizePolicy.Policy.Expanding,
                                               QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.quit_button.setDefault(False)
        self.quit_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.quit_button)
        self.sign_up_button = QtWidgets.QPushButton('Sign up')
        self.sign_up_button.setObjectName('blue_button')
        self.sign_up_button.setDefault(True)
        self.sign_up_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.sign_up_button)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_up_button.clicked.connect(self.apply)
        self.profile_picture_button.clicked.connect(
            self.update_profile_picture)
        self.user_name_lineEdit.textChanged.connect(
            lambda: self.get_random_profile_picture(force=0))

    def apply(self):
        user_name = self.user_name_lineEdit.text()
        password = self.password_lineEdit.text()
        confirm_password = self.password_confirm_lineEdit.text()
        email = self.email_lineEdit.text()
        admin_password = self.admin_password_lineEdit.text()
        championship_participation = self.championship_participation.isChecked()
        if confirm_password == password:
            if repository.create_user(user_name,
                                      password,
                                      email,
                                      admin_password,
                                      self.image_file,
                                      championship_participation):
                self.accept()
        else:
            logger.warning("User passwords doesn't matches")

    def get_random_profile_picture(self, force=0):
        if not self.use_image_file or force:
            user_name = self.user_name_lineEdit.text()
            if user_name == '':
                user_name = ' '
            image_file = image.user_random_image(user_name)
            self.image_file = image_file
            self.update_profile_button()

    def update_profile_button(self):
        icon = QtGui.QIcon()
        pm = gui_utils.mask_image(
            image.convert_image_to_bytes(self.image_file), 'png', 54)
        icon.addPixmap(pm)
        self.profile_picture_button.setIcon(icon)

    def update_profile_picture(self):
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select profile picture", "",
                                                              "All Files (*);;Images Files (*.png);;Images Files (*.jpg);;Images Files (*.jpeg)")
        if image_file:
            extension = image_file.split('.')[-1].upper()
            if (extension == 'PNG') or (extension == 'JPG') or (extension == 'JPEG'):
                self.image_file = image_file
                self.use_image_file = 1
                self.update_profile_button()
            else:
                logger.warning(
                    '{} is not a valid image file...'.format(image_file))
