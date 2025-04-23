# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import time
import copy
import logging
import traceback

# Wizard modules
from wizard.gui import gui_utils

# Wizard gui modules
from wizard.vars import ressources
from wizard.core import image
from wizard.core import repository

logger = logging.getLogger(__name__)


class artefact_interaction_widget(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(artefact_interaction_widget, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Choose target")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.parent = parent
        self.search_thread = search_thread()

        self.user_ids = dict()
        self.user_rows = dict()
        self.user = None
        self.build_ui()
        self.init_icons_dic()
        self.connect_functions()

    def init_icons_dic(self):
        self.icons_dic = dict()
        self.icons_dic['life'] = QtGui.QIcon(ressources._heart_icon_)
        self.icons_dic['coins'] = QtGui.QIcon(ressources._coin_icon_)
        self.icons_dic['level'] = QtGui.QIcon(ressources._level_icon_)

    def update_search(self):
        search_data = self.search_bar.text()
        if search_data != '':
            self.search_thread.update_search(self.user_rows, search_data)
        else:
            self.show_all()

    def show_search_user(self, user_id):
        if user_id in self.user_ids.keys():
            self.user_ids[user_id].setHidden(False)

    def hide_search_user(self, user_id):
        if user_id in self.user_ids.keys():
            self.user_ids[user_id].setHidden(True)

    def show_all(self):
        for user_id in self.user_ids.keys():
            self.user_ids[user_id].setHidden(False)

    def refresh(self):
        user_rows = repository.get_users_list()
        self.user_rows = user_rows
        for user_row in user_rows:
            if not user_row['championship_participation']:
                continue
            if user_row['id'] not in self.user_ids.keys():
                user_item = custom_item(
                    user_row, self.icons_dic, self.list_view.invisibleRootItem())
                self.user_ids[user_row['id']] = user_item
            else:
                if user_row != self.user_ids[user_row['id']].user_row:
                    self.user_ids[user_row['id']].refresh(user_row)

    def showEvent(self, event):
        gui_utils.move_ui(self)
        self.refresh()
        self.search_bar.search_bar.setFocus()
        event.accept()

    def clear(self):
        self.search_bar.setText('')

    def leaveEvent(self, event):
        if self.rect().contains(self.mapFromGlobal(QtCore.QPoint(QtGui.QCursor.pos()))):
            return
        self.reject()

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.update_search)
        self.search_thread.show_id_signal.connect(self.show_search_user)
        self.search_thread.hide_id_signal.connect(self.hide_search_user)
        self.list_view.itemDoubleClicked.connect(self.return_user)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Down:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Up:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Return:
            self.return_user()
        event.accept()

    def return_user(self):
        selected_items = self.list_view.selectedItems()
        if len(selected_items) != 1:
            return
        self.user = self.list_view.selectedItems()[0].user_row['user_name']
        self.accept()

    def build_ui(self):
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                           QtWidgets.QSizePolicy.Policy.Preferred)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('dark_widget')
        self.main_widget.setStyleSheet('border-radius:5px;')
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_widget_layout)
        self.main_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_widget.setGraphicsEffect(self.shadow)

        self.search_bar = gui_utils.search_bar()
        self.search_bar.setPlaceholderText('"j.dupont"')
        self.main_widget_layout.addWidget(self.search_bar)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet(
            'border-top-left-radius:0px;border-top-right-radius:0px;')
        self.list_view.setColumnCount(5)
        self.list_view.setHeaderHidden(False)
        self.list_view.setHeaderLabels(['', '', 'Life', 'Coins', 'Level'])
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().resizeSection(0, 30)
        self.list_view.header().resizeSection(1, 150)
        self.list_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.main_widget_layout.addWidget(self.list_view)


class custom_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, user_row, icons_dic, parent=None):
        super(custom_item, self).__init__(parent)
        self.user_row = user_row
        self.icons_dic = icons_dic
        self.init_icons()
        self.fill_ui()

    def init_icons(self):
        user_icon = QtGui.QIcon()
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(
            self.user_row['profile_picture']), 'png', 30)
        user_icon.addPixmap(pm)
        self.setIcon(0, user_icon)
        self.setIcon(2, self.icons_dic['life'])
        self.setIcon(3, self.icons_dic['coins'])
        self.setIcon(4, self.icons_dic['level'])

    def fill_ui(self):
        self.setText(1, self.user_row['user_name'])
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, f"{self.user_row['life']}%")
        self.setText(3, str(self.user_row['coins']))
        self.setText(4, str(self.user_row['level']))

    def refresh(self, user_row):
        self.user_row = user_row
        self.fill_ui()


class search_thread(QtCore.QThread):

    show_id_signal = pyqtSignal(int)
    hide_id_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, user_rows, search_data):
        self.running = False
        self.search_data = search_data
        self.user_rows = copy.deepcopy(user_rows)
        self.running = True
        self.start()

    def run(self):
        try:
            keywords = self.search_data.split('&')
            for user_row in self.user_rows:

                user_id = user_row['id']
                del user_row['id']
                del user_row['pass']
                del user_row['email']
                del user_row['profile_picture']
                del user_row['xp']
                del user_row['total_xp']
                del user_row['work_time']
                del user_row['comments_count']
                del user_row['deaths']
                del user_row['administrator']
                del user_row['artefacts']
                del user_row['keeped_artefacts']
                del user_row['coins']

                values = list(user_row.values())
                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)

                if all(keyword.upper() in data.upper() for keyword in keywords):
                    self.show_id_signal.emit(user_id)
                else:
                    self.hide_id_signal.emit(user_id)
        except:
            logger.info(str(traceback.format_exc()))
