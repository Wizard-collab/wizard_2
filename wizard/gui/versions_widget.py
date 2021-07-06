# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import os

# Wizard modules
from wizard.core import launch
from wizard.core import assets
from wizard.core import project
from wizard.core import tools
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import confirm_widget

class versions_widget(QtWidgets.QWidget):

    version_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(versions_widget, self).__init__(parent)
        self.version_ids = dict()
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setObjectName('tree_as_list_widget')
        self.tree_widget.setColumnCount(4)
        self.tree_widget.setIndentation(0)
        self.tree_widget.setAlternatingRowColors(True)
        self.tree_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.tree_widget.setHeaderLabels(['Version', 'User', 'Date', 'Comment'])
        self.tree_widget_scrollBar = self.tree_widget.verticalScrollBar()
        self.main_layout.addWidget(self.tree_widget)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.new_version_button = QtWidgets.QPushButton()
        self.new_version_button.setFixedSize(35,35)
        self.new_version_button.setIconSize(QtCore.QSize(16,16))
        self.new_version_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.buttons_layout.addWidget(self.new_version_button)

        self.folder_button = QtWidgets.QPushButton()
        self.folder_button.setFixedSize(35,35)
        self.folder_button.setIcon(QtGui.QIcon(ressources._folder_icon_))
        self.buttons_layout.addWidget(self.folder_button)

        self.archive_button = QtWidgets.QPushButton()
        self.archive_button.setFixedSize(35,35)
        self.archive_button.setIcon(QtGui.QIcon(ressources._archive_icon_))
        self.buttons_layout.addWidget(self.archive_button)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('dark_widget')
        self.infos_layout = QtWidgets.QHBoxLayout()
        self.infos_layout.setContentsMargins(8,8,8,8)
        self.infos_layout.setSpacing(4)
        self.infos_widget.setLayout(self.infos_layout)
        self.main_layout.addWidget(self.infos_widget)

        self.infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.versions_count_label = QtWidgets.QLabel()
        self.versions_count_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.versions_count_label)

        self.selection_count_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.selection_count_label)

    def connect_functions(self):
        self.tree_widget_scrollBar.rangeChanged.connect(lambda: self.tree_widget_scrollBar.setValue(self.tree_widget_scrollBar.maximum()))
        self.tree_widget.currentItemChanged.connect(self.version_changed)
        self.tree_widget.itemDoubleClicked.connect(self.launch)
        self.tree_widget.itemSelectionChanged.connect(self.refresh_infos)
        self.archive_button.clicked.connect(self.archive)
        self.new_version_button.clicked.connect(self.add_empty_version)
        self.folder_button.clicked.connect(self.open_folder)

    def version_changed(self, item):
        if item is not None:
            self.version_changed_signal.emit(item.version_row['name'])

    def launch(self, item):
        if item is not None:
            if len(self.tree_widget.selectedItems()) == 1:
                launch.launch_work_version(item.version_row['id'])

    def archive(self):
        items = self.tree_widget.selectedItems()
        if items is not None:
            if items!=[]:
                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                    for item in items:
                        assets.archive_version(item.version_row['id'])

    def refresh(self):
        versions_rows = project.get_work_versions(self.work_env_id)
        project_versions_id = []
        if versions_rows is not None:
            for version_row in versions_rows:
                project_versions_id.append(version_row['id'])
                if version_row['id'] not in self.version_ids.keys():
                    version_item = custom_version_tree_item(version_row, self.tree_widget.invisibleRootItem())
                    self.version_ids[version_row['id']] = version_item
        version_ids = list(self.version_ids.keys())
        for version_id in version_ids:
            if version_id not in project_versions_id:
                self.remove_version(version_id)
        self.refresh_infos()

    def refresh_infos(self):
        self.versions_count_label.setText(f"{len(self.version_ids.keys())} versions -")
        selection = self.tree_widget.selectedItems()
        self.selection_count_label.setText(f"{len(selection)} selected")

    def remove_version(self, version_id):
        if version_id in self.version_ids.keys():
            item = self.version_ids[version_id]
            self.tree_widget.invisibleRootItem().removeChild(item)
            del self.version_ids[version_id]

    def add_empty_version(self):
        if self.work_env_id is not None:
            assets.add_version(self.work_env_id, 'Empty version')

    def open_folder(self):
        if self.work_env_id is not None:
            os.startfile(assets.get_work_env_path(self.work_env_id))

    def change_work_env(self, work_env_id):
        self.version_ids = dict()
        self.tree_widget.clear()
        self.work_env_id = work_env_id
        self.refresh()
        

class custom_version_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, version_row, parent=None):
        super(custom_version_tree_item, self).__init__(parent)
        self.version_row = version_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.version_row['name'])
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(0, bold_font)
        self.setText(1, self.version_row['creation_user'])
        day, hour = tools.convert_time(self.version_row['creation_time'])
        self.setText(2, f"{day} - {hour}")
        self.setForeground(2, QtGui.QBrush(QtGui.QColor('gray')))
        self.setText(3, self.version_row['comment'])
