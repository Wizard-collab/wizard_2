# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import custom_window

# Wizard modules
from wizard.core import site
from wizard.core import image
from wizard.vars import ressources

class all_users_widget(custom_window.custom_window):
    def __init__(self, parent = None):
        super(all_users_widget, self).__init__(parent)
        self.user_ids = dict()
        self.build_ui()

    def build_ui(self):
        self.main_widget = QtWidgets.QFrame()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setColumnCount(6)
        self.list_view.setIconSize(QtCore.QSize(30,30))
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.list_view.setHeaderLabels(['Profile picture', 'User name', 'Level', 'Life', 'Experience', 'Administrator'])
        #self.list_view.header().resizeSection(3, 150)
        #self.list_view_scrollBar = self.list_view.verticalScrollBar()
        self.main_layout.addWidget(self.list_view)

    def refresh(self):
        all_user_rows = site.get_users_list()
        if all_user_rows is not None:
            for user_row in all_user_rows:
                if user_row['id'] not in self.user_ids.keys():
                    item = custom_user_tree_item(user_row, self.list_view.invisibleRootItem())
                    self.user_ids[user_row['id']] = item
                else:
                    item = self.user_ids[user_row['id']]
                    item.user_row = user_row
                    item.fill_ui()
            master_id = all_user_rows[0]['id']
            self.user_ids[master_id].set_crown()

class custom_user_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, user_row, parent=None):
        super(custom_user_tree_item, self).__init__(parent)
        self.user_row = user_row
        self.setup_ui()
        self.fill_ui()

    def setup_ui(self):
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('#f0605b')))
        self.setForeground(4, QtGui.QBrush(QtGui.QColor('#f79360')))
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)

    def set_crown(self):
        self.setIcon(2, QtGui.QIcon(ressources._crown_icon_))

    def fill_ui(self):
        user_icon = QtGui.QIcon()
        gui_utils.round_icon(user_icon, image.convert_str_data_to_image_bytes(self.user_row['profile_picture']), 30)
        self.setIcon(0, user_icon)
        self.setText(1, self.user_row['user_name'])
        self.setIcon(2, QtGui.QIcon())
        self.setText(2, str(self.user_row['level']))
        self.setText(3, f"{str(self.user_row['life'])}%")
        self.setText(4, f"{str(self.user_row['xp'])}%")
        if self.user_row['administrator']:
            self.setIcon(5, QtGui.QIcon(ressources._admin_badge_))
        else:
            self.setIcon(5, QtGui.QIcon())