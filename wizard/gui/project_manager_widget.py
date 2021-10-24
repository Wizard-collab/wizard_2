# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.core import tools
from wizard.core import user
from wizard.core import image

# Wizard gui modules
from wizard.gui import custom_window
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import logging_widget

class project_manager_widget(custom_window.custom_dialog):
    def __init__(self, parent=None):
        super(project_manager_widget, self).__init__()
        self.add_title('Project manager')
        self.build_ui()
        self.refresh()
        self.connect_functions()

    def build_ui(self):
        self.resize(900,700)
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.icon_view.setObjectName('transparent_icon_view')
        self.icon_view.setSpacing(4)
        self.icon_view.setIconSize(QtCore.QSize(200,200))
        self.icon_view.setMovement(QtWidgets.QListView.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.IconMode)
        self.icon_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.main_layout.addWidget(self.icon_view)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Quit')
        self.buttons_layout.addWidget(self.cancel_button)

        self.open_button = QtWidgets.QPushButton('Open')
        self.open_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.open_button)

    def connect_functions(self):
        self.cancel_button.clicked.connect(self.reject)
        self.open_button.clicked.connect(self.open_project)
        self.icon_view.itemDoubleClicked.connect(self.open_project)

    def open_project(self):
        if len(self.icon_view.selectedItems()) == 1:
            project_name = self.icon_view.itemWidget(self.icon_view.selectedItems()[0]).project_row['project_name']
            self.project_log_widget = project_log_widget(project_name)
            if self.project_log_widget.exec_() == QtWidgets.QDialog.Accepted:
                self.accept()

    def refresh(self):
        project_rows = site.get_projects_list()
        for project_row in project_rows:
            item = QtWidgets.QListWidgetItem()
            widget = project_icon_widget(project_row, self.icon_view)
            item.setSizeHint(widget.sizeHint())
            self.icon_view.addItem(item)
            self.icon_view.setItemWidget(item, widget)

class project_icon_widget(QtWidgets.QFrame):
    def __init__(self, project_row, parent=None):
        super(project_icon_widget, self).__init__(parent)
        self.project_row = project_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6,6,6,6)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.image_label)

        self.project_data_widget = QtWidgets.QWidget()
        self.project_data_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.project_data_widget.setObjectName('transparent_widget')
        self.project_data_layout = QtWidgets.QHBoxLayout()
        self.project_data_layout.setContentsMargins(0,0,0,0)
        self.project_data_layout.setSpacing(6)
        self.project_data_widget.setLayout(self.project_data_layout)
        self.main_layout.addWidget(self.project_data_widget)

        self.project_name_label = QtWidgets.QLabel()
        self.project_name_label.setObjectName('bold_label')
        self.project_name_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.project_data_layout.addWidget(self.project_name_label)

        self.project_data_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.project_path_label = QtWidgets.QLabel()
        self.project_path_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.project_data_layout.addWidget(self.project_path_label)

        self.project_infos_widget = QtWidgets.QWidget()
        self.project_infos_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.project_infos_widget.setObjectName('transparent_widget')
        self.project_infos_layout = QtWidgets.QHBoxLayout()
        self.project_infos_layout.setContentsMargins(0,0,0,0)
        self.project_infos_layout.setSpacing(6)
        self.project_infos_widget.setLayout(self.project_infos_layout)
        self.main_layout.addWidget(self.project_infos_widget)

        self.project_creation_user_label = QtWidgets.QLabel()
        self.project_creation_user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.project_infos_layout.addWidget(self.project_creation_user_label)

        self.project_creation_time_label = QtWidgets.QLabel()
        self.project_creation_user_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.project_creation_time_label.setObjectName('gray_label')
        self.project_infos_layout.addWidget(self.project_creation_time_label)

        self.project_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def fill_ui(self):
        self.project_name_label.setText(self.project_row['project_name'])
        self.project_path_label.setText(self.project_row['project_path'])
        self.project_creation_user_label.setText(self.project_row['creation_user'])

        day, hour = tools.convert_time(self.project_row['creation_time'])
        self.project_creation_time_label.setText(f"{day}, {hour}")
        self.resize(self.sizeHint())

        icon = QtGui.QIcon()
        if self.project_row['project_image'] is not None:
            project_image = image.convert_str_data_to_image_bytes(self.project_row['project_image'])
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(project_image)
            icon = QtGui.QIcon(pixmap)
        self.image_label.setPixmap(icon.pixmap(250))

class project_log_widget(custom_window.custom_dialog):
    def __init__(self, project_name, parent=None):
        super(project_log_widget, self).__init__()
        self.build_ui()
        self.connect_functions()
        self.project_name = project_name
        self.add_title(f"Connect to {project_name}")

    def build_ui(self):
        self.setMinimumWidth(300)
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Cancel")
        self.buttons_layout.addWidget(self.quit_button)
        self.sign_in_button = QtWidgets.QPushButton('Sign in')
        self.sign_in_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.sign_in_button)

        self.logging_widget = logging_widget.logging_widget(self)
        self.main_layout.addWidget(self.logging_widget)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_in_button.clicked.connect(self.apply)

    def apply(self):
        project_password = self.password_lineEdit.text()
        if user.log_project(self.project_name, project_password):
            gui_server.restart_ui()
            self.accept()