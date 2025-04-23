# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import repository
from wizard.core import tools
from wizard.core import user
from wizard.core import image
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import create_project_widget


class project_manager_widget(QtWidgets.QDialog):
    def __init__(self, parent=None, wait_for_restart=False):
        super(project_manager_widget, self).__init__()

        self.wait_for_restart = wait_for_restart

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Project manager")

        self.build_ui()
        self.connect_functions()
        self.refresh()

    def build_ui(self):
        self.resize(900, 700)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.icon_view.setObjectName('transparent_icon_view')
        self.icon_view.setSpacing(4)
        self.icon_view.setMovement(QtWidgets.QListView.Movement.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.icon_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.main_layout.addWidget(self.icon_view)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Quit')
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.cancel_button)

        self.open_button = QtWidgets.QPushButton('Open')
        self.open_button.setObjectName('blue_button')
        self.open_button.setDefault(True)
        self.open_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.open_button)

    def connect_functions(self):
        self.cancel_button.clicked.connect(self.reject)
        self.open_button.clicked.connect(self.open_project)
        self.icon_view.itemDoubleClicked.connect(self.open_project)

    def open_project(self):
        if len(self.icon_view.selectedItems()) == 1:
            if self.icon_view.selectedItems()[0].type == 'project':
                project_name = self.icon_view.itemWidget(self.icon_view.selectedItems()[
                                                         0]).project_row['project_name']
                self.project_log_widget = project_log_widget(
                    project_name, wait_for_restart=self.wait_for_restart)
                if self.project_log_widget.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    self.accept()
            else:
                self.create_project()

    def refresh(self):

        self.icon_view.clear()

        project_rows = repository.get_projects_list()
        for project_row in project_rows:
            item = QtWidgets.QListWidgetItem()
            widget = project_icon_widget(project_row)
            item.setSizeHint(QtCore.QSize(
                widget.sizeHint().width()+8, widget.sizeHint().height()+8))
            item.type = 'project'
            self.icon_view.addItem(item)
            self.icon_view.setItemWidget(item, widget)

        create_project_item = QtWidgets.QListWidgetItem()
        widget = new_project_widget()
        create_project_item.setSizeHint(QtCore.QSize(270, 203))
        create_project_item.type = 'create_project'
        self.icon_view.addItem(create_project_item)
        self.icon_view.setItemWidget(create_project_item, widget)

    def create_project(self):
        self.create_project_widget = create_project_widget.create_project_widget(
            self)
        self.create_project_widget.exec()
        self.refresh()


class new_project_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(new_project_widget, self).__init__(parent)
        self.build_ui()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.image_label)
        self.image_label.setPixmap(QtGui.QIcon(
            ressources._create_project_image_).pixmap(250))

        self.create_project_label = QtWidgets.QLabel('Create a new project')
        self.create_project_label.setObjectName('bold_label')
        self.create_project_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_layout.addWidget(self.create_project_label)


class project_icon_widget(QtWidgets.QFrame):
    def __init__(self, project_row, parent=None):
        super(project_icon_widget, self).__init__(parent)
        self.project_row = project_row
        self.build_ui()
        self.fill_ui()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.image_label = QtWidgets.QLabel()
        self.main_layout.addWidget(self.image_label)

        self.project_data_widget = QtWidgets.QWidget()
        self.project_data_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_data_widget.setObjectName('transparent_widget')
        self.project_data_layout = QtWidgets.QHBoxLayout()
        self.project_data_layout.setContentsMargins(0, 0, 0, 0)
        self.project_data_layout.setSpacing(6)
        self.project_data_widget.setLayout(self.project_data_layout)
        self.main_layout.addWidget(self.project_data_widget)

        self.project_name_label = QtWidgets.QLabel()
        self.project_name_label.setObjectName('bold_label')
        self.project_name_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_data_layout.addWidget(self.project_name_label)

        self.project_data_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.project_path_label = QtWidgets.QLabel()
        self.project_path_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_data_layout.addWidget(self.project_path_label)

        self.project_infos_widget = QtWidgets.QWidget()
        self.project_infos_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_infos_widget.setObjectName('transparent_widget')
        self.project_infos_layout = QtWidgets.QHBoxLayout()
        self.project_infos_layout.setContentsMargins(0, 0, 0, 0)
        self.project_infos_layout.setSpacing(6)
        self.project_infos_widget.setLayout(self.project_infos_layout)
        self.main_layout.addWidget(self.project_infos_widget)

        self.project_creation_user_label = QtWidgets.QLabel()
        self.project_creation_user_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_infos_layout.addWidget(self.project_creation_user_label)

        self.project_creation_time_label = QtWidgets.QLabel()
        self.project_creation_user_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.project_creation_time_label.setObjectName('gray_label')
        self.project_infos_layout.addWidget(self.project_creation_time_label)

        self.project_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

    def fill_ui(self):
        self.project_name_label.setText(self.project_row['project_name'])
        self.project_path_label.setText(self.project_row['project_path'])
        self.project_creation_user_label.setText(
            self.project_row['creation_user'])

        day, hour = tools.convert_time(self.project_row['creation_time'])
        self.project_creation_time_label.setText(f"{day}, {hour}")

        icon = QtGui.QIcon()
        if self.project_row['project_image'] is not None:
            project_image = image.convert_str_data_to_image_bytes(
                self.project_row['project_image'])
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(project_image)
            icon = QtGui.QIcon(pixmap)
        pm = gui_utils.round_corners_image_button(project_image, (250, 141), 3)
        self.image_label.setPixmap(pm)


class project_log_widget(QtWidgets.QDialog):
    def __init__(self, project_name, parent=None, wait_for_restart=False):
        super(project_log_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Log in")

        self.project_name = project_name
        self.wait_for_restart = wait_for_restart

        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setMinimumWidth(300)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel(f"Log in {self.project_name}")
        self.title_label.setObjectName("title_label_2")
        self.main_layout.addWidget(self.title_label)
        self.spaceItem = QtWidgets.QSpacerItem(
            0, 12, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.password_lineEdit = gui_utils.password_lineEdit()
        self.password_lineEdit.setPlaceholderText('Password')
        self.main_layout.addWidget(self.password_lineEdit)

        self.spaceItem = QtWidgets.QSpacerItem(
            100, 12, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.main_layout.addSpacerItem(self.spaceItem)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.quit_button = QtWidgets.QPushButton("Cancel")
        self.quit_button.setDefault(False)
        self.quit_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.quit_button)
        self.sign_in_button = QtWidgets.QPushButton('Sign in')
        self.sign_in_button.setObjectName('blue_button')
        self.sign_in_button.setDefault(True)
        self.sign_in_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.sign_in_button)

    def connect_functions(self):
        self.quit_button.clicked.connect(self.reject)
        self.sign_in_button.clicked.connect(self.apply)

    def apply(self):
        project_password = self.password_lineEdit.text()
        if user.log_project(self.project_name, project_password, wait_for_restart=self.wait_for_restart):
            gui_server.restart_ui()
            self.accept()
