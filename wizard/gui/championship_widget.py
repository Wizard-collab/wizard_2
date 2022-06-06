# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import repository
from wizard.core import image
from wizard.vars import ressources

class championship_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(championship_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard championship")

        self.user_ids = dict()
        self.build_ui()
        self.refresh()

    def build_ui(self):

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_view.setObjectName('tree_as_list_widget_no_hover')
        self.list_view.setColumnCount(5)
        self.list_view.setIconSize(QtCore.QSize(30,30))
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.list_view.setHeaderLabels(['Profile picture', 'User name', 'Level', 'Experience', 'Administrator'])
        self.main_layout.addWidget(self.list_view)

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def clear(self):
        self.list_view.clear()
        self.user_ids = dict()

    def refresh(self):
        self.clear()
        all_user_rows = repository.get_users_list()
        if all_user_rows is not None:
            for user_row in all_user_rows:
                if user_row['id'] not in self.user_ids.keys():
                    item = custom_user_tree_item(user_row, self.list_view.invisibleRootItem())
                    self.user_ids[user_row['id']] = item
                else:
                    item = self.user_ids[user_row['id']]
                    item.user_row = user_row
                    item.fill_ui()
            self.user_ids[all_user_rows[0]['id']].set_crown(1)
            if len(all_user_rows)>=2:
                self.user_ids[all_user_rows[1]['id']].set_crown(2)
            if len(all_user_rows)>=3:
                self.user_ids[all_user_rows[2]['id']].set_crown(3)

class custom_user_tree_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, user_row, parent=None):
        super(custom_user_tree_item, self).__init__(parent)
        self.user_row = user_row
        self.setup_ui()
        self.fill_ui()

    def setup_ui(self):
        self.setForeground(3, QtGui.QBrush(QtGui.QColor('#f79360')))
        bold_font=QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)

    def set_crown(self, crown):
        if crown == 1:
            self.setIcon(2, QtGui.QIcon(ressources._gold_icon_))
        elif crown == 2:
            self.setIcon(2, QtGui.QIcon(ressources._silver_icon_))
        elif crown == 3:
            self.setIcon(2, QtGui.QIcon(ressources._bronze_icon_))

    def fill_ui(self):
        user_icon = QtGui.QIcon()
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(self.user_row['profile_picture']), 'png', 30)
        user_icon.addPixmap(pm)
        self.setIcon(0, user_icon)
        self.setText(1, self.user_row['user_name'])
        self.setIcon(2, QtGui.QIcon())
        self.setText(2, str(self.user_row['level']))
        self.setText(3, f"{str(self.user_row['total_xp'])}")
        if self.user_row['administrator']:
            self.setIcon(4, QtGui.QIcon(ressources._admin_badge_))
        else:
            self.setIcon(4, QtGui.QIcon())