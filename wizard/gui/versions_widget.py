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
        self.work_env_id = None
        self.version_tree_ids = dict()
        self.version_icon_ids = dict()
        self.build_ui()
        self.connect_functions()

    def change_work_env(self, work_env_id):
        self.version_tree_ids = dict()
        self.version_icon_ids = dict()
        self.list_view.clear()
        self.icon_view.clear()
        self.work_env_id = work_env_id
        self.refresh()

    def refresh(self):
        self.refresh_tree()
        self.refresh_icons_view()

    def refresh_tree(self):
        if self.list_view.isVisible() == True:
            versions_rows = project.get_work_versions(self.work_env_id)
            project_versions_id = []
            if versions_rows is not None:
                for version_row in versions_rows:
                    project_versions_id.append(version_row['id'])
                    if version_row['id'] not in self.version_tree_ids.keys():
                        version_item = custom_version_tree_item(version_row, self.list_view.invisibleRootItem())
                        self.version_tree_ids[version_row['id']] = version_item
            version_tree_ids = list(self.version_tree_ids.keys())
            for version_id in version_tree_ids:
                if version_id not in project_versions_id:
                    self.remove_tree_version(version_id)
            self.refresh_infos()

    def refresh_icons_view(self):
        if self.icon_view.isVisible() == True:
            versions_rows = project.get_work_versions(self.work_env_id)
            project_versions_id = []
            if versions_rows is not None:
                for version_row in versions_rows:
                    project_versions_id.append(version_row['id'])
                    if version_row['id'] not in self.version_icon_ids.keys():
                        version_item = custom_version_icon_item(version_row)
                        self.icon_view.addItem(version_item)
                        self.version_icon_ids[version_row['id']] = version_item
            version_icon_ids = list(self.version_icon_ids.keys())
            for version_id in version_icon_ids:
                if version_id not in project_versions_id:
                    self.remove_icon_version(version_id)
            self.refresh_infos()

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(4)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.list_view.setHeaderLabels(['Version', 'User', 'Date', 'Comment'])
        self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)
        self.list_view.setVisible(0)

        self.icon_view = QtWidgets.QListWidget()
        self.icon_view.setObjectName('icon_view')
        self.icon_view.setSpacing(4)
        self.icon_view.setIconSize(QtCore.QSize(200,200))
        self.icon_view.setMovement(QtWidgets.QListView.Static)
        self.icon_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.icon_view.setViewMode(QtWidgets.QListView.IconMode)
        self.icon_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.icon_view_scrollBar = self.icon_view.verticalScrollBar()
        self.main_layout.addWidget(self.icon_view)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.toggle_view_button = QtWidgets.QPushButton()
        self.toggle_view_button.setFixedSize(35,35)
        self.toggle_view_button.setIconSize(QtCore.QSize(27,27))
        self.toggle_view_button.setIcon(QtGui.QIcon(ressources._list_view_icon_))
        self.buttons_layout.addWidget(self.toggle_view_button)

        self.duplicate_button = QtWidgets.QPushButton()
        self.duplicate_button.setFixedSize(35,35)
        self.duplicate_button.setIcon(QtGui.QIcon(ressources._duplicate_icon_))
        self.buttons_layout.addWidget(self.duplicate_button)

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
        self.list_view_scrollBar.rangeChanged.connect(lambda: self.list_view_scrollBar.setValue(self.list_view_scrollBar.maximum()))
        self.icon_view_scrollBar.rangeChanged.connect(lambda: self.icon_view_scrollBar.setValue(self.icon_view_scrollBar.maximum()))
        self.list_view.currentItemChanged.connect(self.version_changed)
        self.list_view.itemDoubleClicked.connect(self.launch)
        self.list_view.itemSelectionChanged.connect(self.refresh_infos)

        self.icon_view.currentItemChanged.connect(self.version_changed)
        self.icon_view.itemDoubleClicked.connect(self.launch)
        self.icon_view.itemSelectionChanged.connect(self.refresh_infos)

        self.archive_button.clicked.connect(self.archive)
        self.duplicate_button.clicked.connect(self.duplicate_version)
        self.new_version_button.clicked.connect(self.add_empty_version)
        self.folder_button.clicked.connect(self.open_folder)
        self.toggle_view_button.clicked.connect(self.toggle_view)

    def version_changed(self, item):
        if item is not None:
            self.version_changed_signal.emit(item.version_row['name'])

    def toggle_view(self):
        vis = self.icon_view.isVisible()
        self.icon_view.setVisible(1-vis)
        self.list_view.setVisible(vis)
        if not vis:
            self.toggle_view_button.setIcon(QtGui.QIcon(ressources._list_view_icon_))
        else:
            self.toggle_view_button.setIcon(QtGui.QIcon(ressources._icon_view_icon_))
        self.refresh()

    def get_number(self):
        number = 0
        if self.icon_view.isVisible() == True:
            number = len(self.version_icon_ids)
        elif self.list_view.isVisible() == True:
            number = len(self.version_tree_ids)
        return number

    def get_selection(self):
        selection = None
        if self.icon_view.isVisible() == True:
            selection = self.icon_view.selectedItems()
        elif self.list_view.isVisible() == True:
            selection = self.list_view.selectedItems()
        return selection

    def duplicate_version(self):
        selection = self.get_selection()
        if selection is not None:
            for item in selection:
                assets.duplicate_version(item.version_row['id'], f"Duplicate from version {item.version_row['name']}")

    def launch(self, item):
        if item is not None:
            if len(self.get_selection()) == 1:
                launch.launch_work_version(item.version_row['id'])

    def archive(self):
        items = self.get_selection()
        if items is not None:
            if items!=[]:
                self.confirm_widget = confirm_widget.confirm_widget('Do you want to continue ?', parent=self)
                if self.confirm_widget.exec_() == QtWidgets.QDialog.Accepted:
                    for item in items:
                        assets.archive_version(item.version_row['id'])

    def refresh_infos(self):
        self.versions_count_label.setText(f"{self.get_number()} versions -")
        selection = self.get_selection()
        if selection is not None:
            number = len(selection)
        else:
            number = 0
        self.selection_count_label.setText(f"{number} selected")

    def remove_tree_version(self, version_id):
        if version_id in self.version_tree_ids.keys():
            item = self.version_tree_ids[version_id]
            self.list_view.invisibleRootItem().removeChild(item)
            del self.version_tree_ids[version_id]

    def remove_icon_version(self, version_id):
        if version_id in self.version_icon_ids.keys():
            item = self.version_icon_ids[version_id]
            self.icon_view.takeItem(self.icon_view.row(item))
            del self.version_icon_ids[version_id]

    def add_empty_version(self):
        if self.work_env_id is not None:
            assets.add_version(self.work_env_id, 'Empty version')

    def open_folder(self):
        if self.work_env_id is not None:
            os.startfile(assets.get_work_env_path(self.work_env_id))

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

class custom_version_icon_item(QtWidgets.QListWidgetItem):
    def __init__(self, version_row, parent=None):
        super(custom_version_icon_item, self).__init__(parent)
        self.version_row = version_row
        self.fill_ui()

    def fill_ui(self):
        icon_path = self.version_row['thumbnail_path']
        if not os.path.isfile(icon_path):
            icon_path = ressources._no_screenshot_small_
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(icon_path)
        icon.addPixmap(pixmap, QtGui.QIcon.Normal)
        icon.addPixmap(pixmap, QtGui.QIcon.Selected)
        self.setIcon(icon)
        self.setText(f"{self.version_row['name']} - {self.version_row['creation_user']}")
        self.setTextAlignment(QtCore.Qt.AlignLeft)
