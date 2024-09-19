# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import os
import logging

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import custom_tab_widget

# Wizard modules
from wizard.vars import ressources
from wizard.core import application
from wizard.core import user
from wizard.core import repository
from wizard.core import environment
from wizard.core import image
from wizard.core import path_utils
from wizard.core import socket_utils

logger = logging.getLogger(__name__)

class user_preferences_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(user_preferences_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Preferences")

        self.general_widget = general_widget()
        self.user_account_widget = user_account_widget()

        self.build_ui()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
            else:
                self.close()
        else:
            self.show()
            self.raise_()

    def showEvent(self, event):
        self.refresh()

    def refresh(self):
        if self.isVisible():
            self.general_widget.refresh()
            self.user_account_widget.refresh()

    def build_ui(self):
        self.resize(600,800)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.tabs_widget = custom_tab_widget.custom_tab_widget()
        self.main_layout.addWidget(self.tabs_widget)

        self.general_tab_index = self.tabs_widget.addTab(self.general_widget, 'General', QtGui.QIcon(ressources._settings_icon_))
        self.account_tab_index = self.tabs_widget.addTab(self.user_account_widget, 'Account', QtGui.QIcon(ressources._user_icon_))

class general_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(general_widget, self).__init__(parent)
        self.ignore_admin_toggle = 0
        self.build_ui()
        self.connect_functions()

    def refresh(self):
        team_dns = environment.get_team_dns()
        if team_dns is not None:
            self.team_host_lineEdit.setText(team_dns[0])
            self.team_port_lineEdit.setText(str(team_dns[1]))
        else:
            self.team_host_lineEdit.clear()
            self.team_port_lineEdit.clear()

        local_path = user.user().get_local_path()
        if local_path:
            self.local_path_lineEdit.setText(local_path)
        else:
            self.local_path_lineEdit.clear()

        popups_enabled = user.user().get_popups_enabled()
        popups_blink_enabled = user.user().get_popups_blink_enabled()
        keep_until_comment = user.user().get_keep_until_comment()
        popups_duration = user.user().get_popups_duration()
        self.enable_popups_checkbox.setChecked(popups_enabled)
        self.enable_popups_blink_checkbox.setChecked(popups_blink_enabled)
        self.keep_until_comment_checkbox.setChecked(keep_until_comment)
        self.popups_duration_spinBox.setValue(popups_duration)

        app_scale = int(float(user.user().get_app_scale())*100)
        self.app_scale_spinBox.setValue(app_scale)

        self.install_dir_data.setText(path_utils.abspath(''))
        version_dic = application.get_version()
        self.version_data.setText(f"{version_dic['MAJOR']}.{version_dic['MINOR']}.{version_dic['PATCH']}")
        self.build_data.setText(str(version_dic['builds']))

        psql_dns = environment.get_psql_dns()
        psql_host = psql_dns.split(' ')[0].split('=')[-1]
        psql_port = psql_dns.split(' ')[1].split('=')[-1]
        psql_user = psql_dns.split(' ')[2].split('=')[-1]
        self.psql_host_data.setText(psql_host)
        self.psql_port_data.setText(psql_port)
        self.psql_user_data.setText(psql_user)

        repository_db = environment.get_repository()[11:]
        self.repository_data.setText(repository_db)

        local_ip = socket_utils.get_local_ip()
        self.local_ip_label.setText(f"My local ip : {local_ip}")

    def apply_popups_settings(self):
        popups_enabled = self.enable_popups_checkbox.isChecked()
        blink = self.enable_popups_blink_checkbox.isChecked()
        keep_until_comment = self.keep_until_comment_checkbox.isChecked()
        popups_duration = self.popups_duration_spinBox.value()
        user.user().set_popups_settings(popups_enabled,
                                            blink,
                                            popups_duration,
                                            keep_until_comment)

    def apply_local_path(self):
        local_path = self.local_path_lineEdit.text()
        if user.user().set_local_path(local_path):
            self.refresh()

    def apply_app_scale(self):
        app_scale = str(self.app_scale_spinBox.value()/100)
        if user.user().set_app_scale(app_scale):
            gui_server.restart_ui()

    def apply_team_dns(self):
        host = self.team_host_lineEdit.text()
        port = self.team_port_lineEdit.text()
        process = 1
        try:
            port = int(port)
        except:
            logger.warning('Please enter a valid port')
            process = 0
        if port == '':
            logger.warning('Please enter a valid port')
            process = 0
        if host == '':
            logger.warning('Please enter a valid host')
            process = 0
        if process:
            if user.user().set_team_dns(host, port):
                self.refresh()

    def connect_functions(self):
        self.team_ip_accept_button.clicked.connect(self.apply_team_dns)
        self.local_path_accept_button.clicked.connect(self.apply_local_path)
        self.folder_button.clicked.connect(self.open_explorer)
        self.enable_popups_checkbox.stateChanged.connect(self.apply_popups_settings)
        self.enable_popups_blink_checkbox.stateChanged.connect(self.apply_popups_settings)
        self.keep_until_comment_checkbox.stateChanged.connect(self.apply_popups_settings)
        self.popups_duration_spinBox.valueChanged.connect(self.apply_popups_settings)
        self.app_scale_accept_button.clicked.connect(self.apply_app_scale)

    def open_explorer(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open local project directory",
                                       "",
                                       QtWidgets.QFileDialog.Option.ShowDirsOnly
                                       | QtWidgets.QFileDialog.Option.DontResolveSymlinks)
        if project_path:
            self.local_path_lineEdit.setText(project_path)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_widget.setObjectName('transparent_widget')
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setContentsMargins(24,24,24,24)
        self.scrollArea_layout.setSpacing(12)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)

        self.main_layout.addWidget(self.scrollArea)

        self.general_settings_title = QtWidgets.QLabel('General')
        self.general_settings_title.setObjectName('title_label')
        self.scrollArea_layout.addWidget(self.general_settings_title)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.popups_frame = QtWidgets.QFrame()
        self.popups_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.popups_layout = QtWidgets.QVBoxLayout()
        self.popups_layout.setContentsMargins(0,0,0,0)
        self.popups_layout.setSpacing(6)
        self.popups_frame.setLayout(self.popups_layout)
        self.scrollArea_layout.addWidget(self.popups_frame)

        self.popups_title = QtWidgets.QLabel('Popups')
        self.popups_title.setObjectName('bold_label')
        self.popups_layout.addWidget(self.popups_title)

        self.popups_subwidget = QtWidgets.QWidget()
        self.popups_sublayout = QtWidgets.QFormLayout()
        self.popups_sublayout.setContentsMargins(0,0,0,0)
        self.popups_sublayout.setSpacing(6)
        self.popups_subwidget.setLayout(self.popups_sublayout)
        self.popups_layout.addWidget(self.popups_subwidget)

        self.enable_popups_checkbox = QtWidgets.QCheckBox()
        self.enable_popups_checkbox.setObjectName('android_checkbox')
        self.popups_sublayout.addRow(QtWidgets.QLabel('Popups enabled'), self.enable_popups_checkbox)

        self.enable_popups_blink_checkbox = QtWidgets.QCheckBox()
        self.enable_popups_blink_checkbox.setObjectName('android_checkbox')
        self.popups_sublayout.addRow(QtWidgets.QLabel('Popups blink enabled'), self.enable_popups_blink_checkbox)

        self.keep_until_comment_checkbox = QtWidgets.QCheckBox()
        self.keep_until_comment_checkbox.setObjectName('android_checkbox')
        self.popups_sublayout.addRow(QtWidgets.QLabel('Keep popups until comment'), self.keep_until_comment_checkbox)

        self.popups_duration_spinBox = QtWidgets.QSpinBox()
        self.popups_duration_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.popups_sublayout.addRow(QtWidgets.QLabel('Duration ( seconds )'), self.popups_duration_spinBox)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.app_scale_frame = QtWidgets.QFrame()
        self.app_scale_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.app_scale_layout = QtWidgets.QVBoxLayout()
        self.app_scale_layout.setContentsMargins(0,0,0,0)
        self.app_scale_layout.setSpacing(6)
        self.app_scale_frame.setLayout(self.app_scale_layout)
        self.scrollArea_layout.addWidget(self.app_scale_frame)

        self.app_scale_sublayout = QtWidgets.QFormLayout()
        self.app_scale_sublayout.setContentsMargins(0,0,0,0)
        self.app_scale_sublayout.setSpacing(6)
        self.app_scale_layout.addLayout(self.app_scale_sublayout)

        self.app_scale_spinBox = QtWidgets.QSpinBox()
        self.app_scale_spinBox.setRange(50,150)
        self.app_scale_spinBox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.app_scale_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.app_scale_sublayout.addRow(QtWidgets.QLabel('App scale ( % )'), self.app_scale_spinBox)

        self.app_scale_buttons_layout = QtWidgets.QHBoxLayout()
        self.app_scale_buttons_layout.setContentsMargins(0,0,0,0)
        self.app_scale_buttons_layout.setSpacing(6)
        self.app_scale_layout.addLayout(self.app_scale_buttons_layout)

        self.app_scale_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.app_scale_accept_button = QtWidgets.QPushButton('Apply ( Will restart )')
        self.app_scale_accept_button.setObjectName('blue_button')
        self.app_scale_buttons_layout.addWidget(self.app_scale_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.local_path_frame = QtWidgets.QFrame()
        self.local_path_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.local_path_layout = QtWidgets.QVBoxLayout()
        self.local_path_layout.setContentsMargins(0,0,0,0)
        self.local_path_layout.setSpacing(6)
        self.local_path_frame.setLayout(self.local_path_layout)
        self.scrollArea_layout.addWidget(self.local_path_frame)

        self.local_path_title = QtWidgets.QLabel('Local path')
        self.local_path_title.setObjectName('bold_label')
        self.local_path_layout.addWidget(self.local_path_title)

        self.local_path_subwidget = QtWidgets.QWidget()
        self.local_path_subwidget_layout = QtWidgets.QHBoxLayout()
        self.local_path_subwidget_layout.setContentsMargins(0,0,0,0)
        self.local_path_subwidget_layout.setSpacing(6)
        self.local_path_subwidget.setLayout(self.local_path_subwidget_layout)
        self.local_path_layout.addWidget(self.local_path_subwidget)

        self.local_path_lineEdit = QtWidgets.QLineEdit()
        self.local_path_lineEdit.setPlaceholderText('Local project directory')
        self.local_path_subwidget_layout.addWidget(self.local_path_lineEdit)

        self.folder_button = QtWidgets.QPushButton()
        self.folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.folder_button.setIconSize(QtCore.QSize(20,20))
        self.folder_button.setFixedSize(28,28)
        self.local_path_subwidget_layout.addWidget(self.folder_button)

        self.local_path_buttons_widget = QtWidgets.QWidget()
        self.local_path_buttons_layout = QtWidgets.QHBoxLayout()
        self.local_path_buttons_layout.setContentsMargins(0,0,0,0)
        self.local_path_buttons_layout.setSpacing(6)
        self.local_path_buttons_widget.setLayout(self.local_path_buttons_layout)
        self.local_path_layout.addWidget(self.local_path_buttons_widget)

        self.local_path_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.local_path_accept_button = QtWidgets.QPushButton('Apply')
        self.local_path_accept_button.setObjectName('blue_button')
        self.local_path_buttons_layout.addWidget(self.local_path_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.team_ip_frame = QtWidgets.QFrame()
        self.team_ip_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.team_ip_layout = QtWidgets.QVBoxLayout()
        self.team_ip_layout.setContentsMargins(0,0,0,0)
        self.team_ip_layout.setSpacing(6)
        self.team_ip_frame.setLayout(self.team_ip_layout)
        self.scrollArea_layout.addWidget(self.team_ip_frame)

        self.team_ip_title = QtWidgets.QLabel('Team server DNS')
        self.team_ip_title.setObjectName('bold_label')
        self.team_ip_layout.addWidget(self.team_ip_title)

        self.local_ip_label = QtWidgets.QLabel()
        self.local_ip_label.setObjectName('gray_label')
        self.team_ip_layout.addWidget(self.local_ip_label)

        self.team_host_lineEdit = QtWidgets.QLineEdit()
        self.team_host_lineEdit.setPlaceholderText('Host ( ex: 127.0.0.1 )')
        self.team_ip_layout.addWidget(self.team_host_lineEdit)

        self.team_port_lineEdit = QtWidgets.QLineEdit()
        self.team_port_lineEdit.setPlaceholderText('Port ( ex: 11111 )')
        self.team_ip_layout.addWidget(self.team_port_lineEdit)

        self.team_ip_buttons_widget = QtWidgets.QWidget()
        self.team_ip_buttons_layout = QtWidgets.QHBoxLayout()
        self.team_ip_buttons_layout.setContentsMargins(0,0,0,0)
        self.team_ip_buttons_layout.setSpacing(6)
        self.team_ip_buttons_widget.setLayout(self.team_ip_buttons_layout)
        self.team_ip_layout.addWidget(self.team_ip_buttons_widget)

        self.team_ip_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.team_ip_accept_button = QtWidgets.QPushButton('Apply')
        self.team_ip_accept_button.setObjectName('blue_button')
        self.team_ip_buttons_layout.addWidget(self.team_ip_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.about_frame = QtWidgets.QFrame()
        self.about_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.about_layout = QtWidgets.QVBoxLayout()
        self.about_layout.setContentsMargins(0,0,0,0)
        self.about_layout.setSpacing(6)
        self.about_frame.setLayout(self.about_layout)
        self.scrollArea_layout.addWidget(self.about_frame)

        self.about_title = QtWidgets.QLabel('About')
        self.about_title.setObjectName('bold_label')
        self.about_layout.addWidget(self.about_title)

        self.about_subwidget = QtWidgets.QWidget()
        self.about_sublayout = QtWidgets.QFormLayout()
        self.about_sublayout.setContentsMargins(0,0,0,0)
        self.about_sublayout.setSpacing(6)
        self.about_subwidget.setLayout(self.about_sublayout)
        self.about_layout.addWidget(self.about_subwidget)

        self.install_dir_label = QtWidgets.QLabel('Install directory')
        self.install_dir_label.setObjectName('gray_label')
        self.install_dir_data = QtWidgets.QLabel()
        self.install_dir_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.about_sublayout.addRow(self.install_dir_label, self.install_dir_data)

        self.version_label = QtWidgets.QLabel('Version')
        self.version_label.setObjectName('gray_label')
        self.version_data = QtWidgets.QLabel()
        self.version_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.about_sublayout.addRow(self.version_label, self.version_data)

        self.build_label = QtWidgets.QLabel('Build')
        self.build_label.setObjectName('gray_label')
        self.build_data = QtWidgets.QLabel()
        self.build_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.about_sublayout.addRow(self.build_label, self.build_data)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.psql_frame = QtWidgets.QFrame()
        self.psql_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.psql_layout = QtWidgets.QVBoxLayout()
        self.psql_layout.setContentsMargins(0,0,0,0)
        self.psql_layout.setSpacing(6)
        self.psql_frame.setLayout(self.psql_layout)
        self.scrollArea_layout.addWidget(self.psql_frame)

        self.psql_title = QtWidgets.QLabel('PostgreSQL - DNS')
        self.psql_title.setObjectName('bold_label')
        self.psql_layout.addWidget(self.psql_title)

        self.psql_subwidget = QtWidgets.QWidget()
        self.psql_sublayout = QtWidgets.QFormLayout()
        self.psql_sublayout.setContentsMargins(0,0,0,0)
        self.psql_sublayout.setSpacing(6)
        self.psql_subwidget.setLayout(self.psql_sublayout)
        self.psql_layout.addWidget(self.psql_subwidget)

        self.psql_host_label = QtWidgets.QLabel('Host')
        self.psql_host_label.setObjectName('gray_label')
        self.psql_host_data = QtWidgets.QLabel()
        self.psql_host_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.psql_sublayout.addRow(self.psql_host_label, self.psql_host_data)

        self.psql_port_label = QtWidgets.QLabel('Port')
        self.psql_port_label.setObjectName('gray_label')
        self.psql_port_data = QtWidgets.QLabel()
        self.psql_port_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.psql_sublayout.addRow(self.psql_port_label, self.psql_port_data)

        self.psql_user_label = QtWidgets.QLabel('User')
        self.psql_user_label.setObjectName('gray_label')
        self.psql_user_data = QtWidgets.QLabel()
        self.psql_user_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.psql_sublayout.addRow(self.psql_user_label, self.psql_user_data)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.repository_frame = QtWidgets.QFrame()
        self.repository_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.repository_layout = QtWidgets.QVBoxLayout()
        self.repository_layout.setContentsMargins(0,0,0,0)
        self.repository_layout.setSpacing(6)
        self.repository_frame.setLayout(self.repository_layout)
        self.scrollArea_layout.addWidget(self.repository_frame)

        self.repository_title = QtWidgets.QLabel('repository Database')
        self.repository_title.setObjectName('bold_label')
        self.repository_layout.addWidget(self.repository_title)

        self.repository_subwidget = QtWidgets.QWidget()
        self.repository_sublayout = QtWidgets.QFormLayout()
        self.repository_sublayout.setContentsMargins(0,0,0,0)
        self.repository_sublayout.setSpacing(6)
        self.repository_subwidget.setLayout(self.repository_sublayout)
        self.repository_layout.addWidget(self.repository_subwidget)

        self.repository_label = QtWidgets.QLabel('repository')
        self.repository_label.setObjectName('gray_label')
        self.repository_data = QtWidgets.QLabel()
        self.repository_data.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.repository_sublayout.addRow(self.repository_label, self.repository_data)

        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

class user_account_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(user_account_widget, self).__init__(parent)
        self.ignore_admin_toggle = 0
        self.build_ui()
        self.refresh()
        self.connect_functions()

    def refresh(self):
        self.ignore_admin_toggle = 1
        user_name = environment.get_user()
        user_row = repository.get_user_row_by_name(user_name)
        self.user_name_label.setText(user_name)
        self.user_email_label.setText(user_row['email'])

        #self.admin_checkBox.setCheckState(user_row['administrator'])
        self.admin_checkBox.setChecked(user_row['administrator'])

        profile_image = image.convert_str_data_to_image_bytes(user_row['profile_picture'])
        pm = QtGui.QPixmap()
        pm.loadFromData(profile_image, 'png')
        self.profile_picture_button.setIcon(QtGui.QIcon(pm))

        self.email_lineEdit.clear()
        self.old_pwd_lineEdit.clear()
        self.new_pwd_lineEdit.clear()
        self.confirm_pwd_lineEdit.clear()
        self.admin_password_lineEdit.clear()
        self.ignore_admin_toggle = 0

    def connect_functions(self):
        self.email_accept_button.clicked.connect(self.apply_new_email)
        self.pwd_accept_button.clicked.connect(self.change_password)
        self.admin_checkBox.stateChanged.connect(self.modify_user_privileges)
        self.profile_picture_button.clicked.connect(self.update_profile_picture)

    def apply_new_email(self):
        new_email = self.email_lineEdit.text()
        if repository.modify_user_email(environment.get_user(), new_email):
            self.refresh()

    def change_password(self):
        old_password = self.old_pwd_lineEdit.text()
        new_password = self.new_pwd_lineEdit.text()
        confirm_password = self.confirm_pwd_lineEdit.text()
        process = 1
        if new_password != confirm_password:
            logger.warning("The new passwords doesn't matches")
            process = 0
        if new_password == '' or confirm_password == '':
            logger.warning("Please enter a new password")
            process = 0
        if process:
            if repository.modify_user_password(environment.get_user(), old_password, new_password):
                self.refresh()

    def modify_user_privileges(self):
        if not self.ignore_admin_toggle:
            requested_privilege = self.admin_checkBox.isChecked()
            admin_pwd = self.admin_password_lineEdit.text()
            if requested_privilege:
                repository.upgrade_user_privilege(environment.get_user(), admin_pwd)
            else:
                repository.downgrade_user_privilege(environment.get_user(), admin_pwd)
            self.refresh()

    def update_profile_picture(self):
        image_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select profile picture", "",
                            "All Files (*);;Images Files (*.png);;Images Files (*.jpg);;Images Files (*.jpeg)")
        if image_file:
            extension = image_file.split('.')[-1].upper()
            if (extension == 'PNG') or (extension == 'JPG') or (extension == 'JPEG'):
                repository.modify_user_profile_picture(environment.get_user(), image_file)
                self.refresh()
            else:
                logger.warning('{} is not a valid image file...'.format(image_file))

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollBar = self.scrollArea.verticalScrollBar()

        self.scrollArea_widget = QtWidgets.QWidget()
        self.scrollArea_widget.setObjectName('transparent_widget')
        self.scrollArea_layout = QtWidgets.QVBoxLayout()
        self.scrollArea_layout.setContentsMargins(24,24,24,24)
        self.scrollArea_layout.setSpacing(12)
        self.scrollArea_widget.setLayout(self.scrollArea_layout)

        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollArea_widget)

        self.main_layout.addWidget(self.scrollArea)

        self.account_settings_title = QtWidgets.QLabel('Account')
        self.account_settings_title.setObjectName('title_label')
        self.scrollArea_layout.addWidget(self.account_settings_title)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.profile_frame = QtWidgets.QFrame()
        self.profile_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.profile_layout = QtWidgets.QVBoxLayout()
        self.profile_layout.setContentsMargins(0,0,0,0)
        self.profile_layout.setSpacing(6)
        self.profile_frame.setLayout(self.profile_layout)
        self.scrollArea_layout.addWidget(self.profile_frame)

        self.profile_title = QtWidgets.QLabel('Profile')
        self.profile_title.setObjectName('bold_label')
        self.profile_layout.addWidget(self.profile_title)

        self.profile_subwidget = QtWidgets.QWidget()
        self.profile_subwidget_layout = QtWidgets.QHBoxLayout()
        self.profile_subwidget_layout.setContentsMargins(0,0,0,0)
        self.profile_subwidget_layout.setSpacing(6)
        self.profile_subwidget.setLayout(self.profile_subwidget_layout)
        self.profile_layout.addWidget(self.profile_subwidget)

        self.profile_picture_button = QtWidgets.QPushButton()
        self.profile_picture_button.setFixedSize(60,60)
        self.profile_picture_button.setIconSize(QtCore.QSize(54,54))
        self.profile_subwidget_layout.addWidget(self.profile_picture_button)

        self.profile_sub_subwidget = QtWidgets.QWidget()
        self.profile_sub_subwidget_layout = QtWidgets.QVBoxLayout()
        self.profile_sub_subwidget_layout.setContentsMargins(0,0,0,0)
        self.profile_sub_subwidget_layout.setSpacing(6)
        self.profile_sub_subwidget.setLayout(self.profile_sub_subwidget_layout)
        self.profile_subwidget_layout.addWidget(self.profile_sub_subwidget)

        self.user_name_label = QtWidgets.QLabel('User name')
        self.profile_sub_subwidget_layout.addWidget(self.user_name_label)

        self.user_email_label = QtWidgets.QLabel('User email')
        self.user_email_label.setObjectName('gray_label')
        self.profile_sub_subwidget_layout.addWidget(self.user_email_label)

        self.profile_sub_subwidget_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.email_frame = QtWidgets.QFrame()
        self.email_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.email_layout = QtWidgets.QVBoxLayout()
        self.email_layout.setContentsMargins(0,0,0,0)
        self.email_layout.setSpacing(6)
        self.email_frame.setLayout(self.email_layout)
        self.scrollArea_layout.addWidget(self.email_frame)

        self.email_title = QtWidgets.QLabel('Change email')
        self.email_title.setObjectName('bold_label')
        self.email_layout.addWidget(self.email_title)

        self.email_lineEdit = QtWidgets.QLineEdit()
        self.email_lineEdit.setPlaceholderText('New email')
        self.email_layout.addWidget(self.email_lineEdit)

        self.email_buttons_widget = QtWidgets.QWidget()
        self.email_buttons_layout = QtWidgets.QHBoxLayout()
        self.email_buttons_layout.setContentsMargins(0,0,0,0)
        self.email_buttons_layout.setSpacing(6)
        self.email_buttons_widget.setLayout(self.email_buttons_layout)
        self.email_layout.addWidget(self.email_buttons_widget)

        self.email_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.email_accept_button = QtWidgets.QPushButton('Apply')
        self.email_accept_button.setObjectName('blue_button')
        self.email_buttons_layout.addWidget(self.email_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.pwd_frame = QtWidgets.QFrame()
        self.pwd_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.pwd_layout = QtWidgets.QVBoxLayout()
        self.pwd_layout.setContentsMargins(0,0,0,0)
        self.pwd_layout.setSpacing(6)
        self.pwd_frame.setLayout(self.pwd_layout)
        self.scrollArea_layout.addWidget(self.pwd_frame)

        self.pwd_title = QtWidgets.QLabel('Change password')
        self.pwd_title.setObjectName('bold_label')
        self.pwd_layout.addWidget(self.pwd_title)

        self.old_pwd_lineEdit = gui_utils.password_lineEdit()
        self.old_pwd_lineEdit.setPlaceholderText('Old password')
        self.pwd_layout.addWidget(self.old_pwd_lineEdit)

        self.new_pwd_lineEdit = gui_utils.password_lineEdit()
        self.new_pwd_lineEdit.setPlaceholderText('New password')
        self.pwd_layout.addWidget(self.new_pwd_lineEdit)

        self.confirm_pwd_lineEdit = gui_utils.password_lineEdit()
        self.confirm_pwd_lineEdit.setPlaceholderText('Confirm password')
        self.pwd_layout.addWidget(self.confirm_pwd_lineEdit)

        self.pwd_buttons_widget = QtWidgets.QWidget()
        self.pwd_buttons_layout = QtWidgets.QHBoxLayout()
        self.pwd_buttons_layout.setContentsMargins(0,0,0,0)
        self.pwd_buttons_layout.setSpacing(6)
        self.pwd_buttons_widget.setLayout(self.pwd_buttons_layout)
        self.pwd_layout.addWidget(self.pwd_buttons_widget)

        self.pwd_buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.pwd_accept_button = QtWidgets.QPushButton('Apply')
        self.pwd_accept_button.setObjectName('blue_button')
        self.pwd_buttons_layout.addWidget(self.pwd_accept_button)

        self.scrollArea_layout.addWidget(gui_utils.separator())

        self.admin_frame = QtWidgets.QFrame()
        self.admin_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.admin_layout = QtWidgets.QVBoxLayout()
        self.admin_layout.setContentsMargins(0,0,0,0)
        self.admin_layout.setSpacing(6)
        self.admin_frame.setLayout(self.admin_layout)
        self.scrollArea_layout.addWidget(self.admin_frame)

        self.admin_title = QtWidgets.QLabel('Administrator status')
        self.admin_title.setObjectName('bold_label')
        self.admin_layout.addWidget(self.admin_title)

        self.admin_subwidget = QtWidgets.QWidget()
        self.admin_subwidget_layout = QtWidgets.QHBoxLayout()
        self.admin_subwidget_layout.setContentsMargins(0,0,0,0)
        self.admin_subwidget_layout.setSpacing(6)
        self.admin_subwidget.setLayout(self.admin_subwidget_layout)
        self.admin_layout.addWidget(self.admin_subwidget)

        self.admin_password_lineEdit = gui_utils.password_lineEdit()
        self.admin_password_lineEdit.setPlaceholderText('Administrator password')
        self.admin_subwidget_layout.addWidget(self.admin_password_lineEdit)

        self.admin_checkBox = QtWidgets.QCheckBox()
        self.admin_checkBox.setObjectName('android_checkbox')
        self.admin_subwidget_layout.addWidget(self.admin_checkBox)


        self.scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))
