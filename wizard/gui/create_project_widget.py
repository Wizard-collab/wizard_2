# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import logging_widget
from wizard.gui import gui_utils
from wizard.gui import custom_window
from wizard.gui import gui_server

# Wizard modules
from wizard.core import user
from wizard.core import project
from wizard.core import environment
from wizard.core import create_project
from wizard.core import db_utils
from wizard.vars import ressources
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class create_project_widget(custom_window.custom_dialog):
    def __init__(self, parent=None):
        super(create_project_widget, self).__init__()
        self.project_path = ''
        self.build_ui()
        self.connect_functions()
        self.add_title("Create a project")

    def build_ui(self):
        self.setMinimumWidth(350)
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.credentials_label = QtWidgets.QLabel("Project credentials")
        self.main_layout.addWidget(self.credentials_label)

        self.project_name_lineEdit = QtWidgets.QLineEdit()
        self.project_name_lineEdit.setPlaceholderText('Project name')
        self.main_layout.addWidget(self.project_name_lineEdit)
        
        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Project password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.password_confirm_lineEdit = gui_utils.password_lineEdit()
        self.password_confirm_lineEdit.setPlaceholderText('Confirm project password')
        self.main_layout.addWidget(self.password_confirm_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.project_path_label = QtWidgets.QLabel("The directory of your project")
        self.main_layout.addWidget(self.project_path_label)

        self.path_widget = QtWidgets.QWidget()
        self.path_layout = QtWidgets.QHBoxLayout()
        self.path_layout.setContentsMargins(0,0,0,0)
        self.path_layout.setSpacing(4)
        self.path_widget.setLayout(self.path_layout)
        self.main_layout.addWidget(self.path_widget)

        self.project_path_lineEdit = QtWidgets.QLineEdit()
        self.project_path_lineEdit.setPlaceholderText('Project path')
        self.project_path_lineEdit.setEnabled(False)
        self.path_layout.addWidget(self.project_path_lineEdit)

        self.folder_button = QtWidgets.QPushButton()
        self.folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.folder_button.setIconSize(QtCore.QSize(20,20))
        self.folder_button.setFixedSize(28,28)
        self.path_layout.addWidget(self.folder_button)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.project_settings_label = QtWidgets.QLabel("Project settings")
        self.main_layout.addWidget(self.project_settings_label)

        self.settings_widget = QtWidgets.QWidget()
        self.settings_layout = QtWidgets.QFormLayout()
        self.settings_layout.setContentsMargins(0,0,0,0)
        self.settings_layout.setSpacing(4)
        self.settings_widget.setLayout(self.settings_layout)
        self.main_layout.addWidget(self.settings_widget)

        self.frame_rate_label = QtWidgets.QLabel('Frame rate')
        self.frame_rate_label.setMinimumWidth(100)
        self.frame_rate_label.setObjectName('gray_label')

        self.format_label = QtWidgets.QLabel('Format')
        self.format_label.setObjectName('gray_label')

        self.frame_rate_spinBox = QtWidgets.QSpinBox()
        self.frame_rate_spinBox.setRange(1, 300)
        self.frame_rate_spinBox.setButtonSymbols(2)
        self.frame_rate_spinBox.setValue(24)
        self.settings_layout.addRow(self.frame_rate_label, self.frame_rate_spinBox)

        self.format_widget = QtWidgets.QWidget()
        self.format_layout = QtWidgets.QHBoxLayout()
        self.format_layout.setContentsMargins(0,0,0,0)
        self.format_layout.setSpacing(4)
        self.format_widget.setLayout(self.format_layout)
        self.settings_layout.addRow(self.format_label, self.format_widget)

        self.format_width = QtWidgets.QSpinBox()
        self.format_width.setRange(1, 100000)
        self.format_width.setButtonSymbols(2)
        self.format_width.setValue(1920)
        self.format_layout.addWidget(self.format_width)

        self.format_height = QtWidgets.QSpinBox()
        self.format_height.setRange(1, 100000)
        self.format_height.setButtonSymbols(2)
        self.format_height.setValue(1080)
        self.format_layout.addWidget(self.format_height)

        self.spaceItem = QtWidgets.QSpacerItem(100,25,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Quit")
        self.buttons_layout.addWidget(self.quit_button)
        self.create_button = QtWidgets.QPushButton('Create project')
        self.create_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.create_button)

        self.logging_widget = logging_widget.logging_widget(self)
        self.main_layout.addWidget(self.logging_widget)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.apply)
        self.project_name_lineEdit.textChanged.connect(self.normalise_project_name)
        self.folder_button.clicked.connect(self.open_explorer)
        self.project_name_lineEdit.textChanged.connect(self.update_project_path)

    def update_project_path(self):
        project_name = self.project_name_lineEdit.text()
        self.project_path_lineEdit.setText(self.project_path+project_name)

    def open_explorer(self):
        project_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open project directory",
                                       "",
                                       QtWidgets.QFileDialog.ShowDirsOnly
                                       | QtWidgets.QFileDialog.DontResolveSymlinks)
        if project_path:
            self.project_path = project_path
            self.update_project_path()

    def normalise_project_name(self, project_name):
        self.project_name_lineEdit.setText(project_name.lower())

    def apply(self):

        old_project_name = environment.get_project_name()

        project_name = self.project_name_lineEdit.text()
        project_path = self.project_path_lineEdit.text()
        password = self.password_lineEdit.text()
        password_confirm = self.password_confirm_lineEdit.text()
        if password == password_confirm:
            if project.create_project(project_name, project_path, password):
                db_utils.modify_db_name('project', project_name)
                create_project.create_project(project_name, project_path, password)
                if old_project_name is not None:
                    user.log_project_without_cred(old_project_name)
                self.accept()
        else:
            logger.warning("Project passwords doesn't matches")