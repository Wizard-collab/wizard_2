# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import json
import statistics

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import create_quote_widget

# Wizard modules
from wizard.core import repository
from wizard.core import tools
from wizard.vars import ressources

class quotes_manager(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(quotes_manager, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Quotes manager")

        self.quotes_ids = dict()
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def connect_functions(self):
        self.create_quote_button.clicked.connect(self.add_quote)

    def build_ui(self):

        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self.setObjectName('dark_widget')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.quotes_scrollArea = QtWidgets.QScrollArea()
        self.quotes_scrollBar = self.quotes_scrollArea.verticalScrollBar()

        self.quotes_scrollArea_widget = QtWidgets.QWidget()
        self.quotes_scrollArea_widget.setObjectName('dark_widget')
        self.quotes_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.quotes_scrollArea_layout.setSpacing(6)
        self.quotes_scrollArea_widget.setLayout(self.quotes_scrollArea_layout)

        self.quotes_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.quotes_scrollArea.setWidgetResizable(True)
        self.quotes_scrollArea.setWidget(self.quotes_scrollArea_widget)

        self.quotes_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))

        self.main_layout.addWidget(self.quotes_scrollArea)

        self.footer_widget = QtWidgets.QWidget()
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_widget.setLayout(self.footer_layout)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(6)
        self.infos_widget.setLayout(self.infos_layout)
        self.footer_layout.addWidget(self.infos_widget)

        self.quotes_number_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.quotes_number_label)

        self.rank_widget = QtWidgets.QWidget()
        self.rank_layout = QtWidgets.QHBoxLayout()
        self.rank_layout.setContentsMargins(0,0,0,0)
        self.rank_layout.setSpacing(2)
        self.rank_widget.setLayout(self.rank_layout)
        self.infos_layout.addWidget(self.rank_widget)

        self.star_icon = QtWidgets.QLabel()
        self.star_icon.setPixmap(QtGui.QIcon(ressources._star_icon_).pixmap(12))
        self.rank_layout.addWidget(self.star_icon)

        self.quote_rank = QtWidgets.QLabel()
        self.rank_layout.addWidget(self.quote_rank)

        self.quote_max = QtWidgets.QLabel('/5  ')
        self.quote_max.setObjectName('gray_label')
        self.rank_layout.addWidget(self.quote_max)

        self.voters_number = QtWidgets.QLabel()
        self.voters_number.setObjectName('gray_label')
        self.rank_layout.addWidget(self.voters_number)

        self.rank_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.create_quote_button = QtWidgets.QPushButton()
        self.create_quote_button.setFixedSize(QtCore.QSize(30,30))
        self.create_quote_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.footer_layout.addWidget(self.create_quote_button)

        self.main_layout.addWidget(self.footer_widget)

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

    def delete_quote(self, quote_id):
        repository.remove_quote(quote_id)
        gui_server.refresh_ui()

    def add_quote(self):
        self.create_quote_widget = create_quote_widget.create_quote_widget(self)
        self.create_quote_widget.exec()
        gui_server.refresh_ui()

    def remove_quote(self, quote_id):
        if quote_id in self.quotes_ids.keys():
            self.quotes_ids[quote_id].setParent(None)
            self.quotes_ids[quote_id].deleteLater()
            del self.quotes_ids[quote_id]

    def refresh(self):
        quotes_rows = repository.get_user_quotes()
        project_quotes = []
        for quote_row in quotes_rows:
            project_quotes.append(quote_row['id'])
            if quote_row['id'] not in self.quotes_ids.keys():
                widget = quote_widget(quote_row)
                widget.delete_signal.connect(self.delete_quote)
                self.quotes_scrollArea_layout.insertWidget(0, widget)
                self.quotes_ids[quote_row['id']] = widget
        quotes_ids = list(self.quotes_ids.keys())
        for quote_id in quotes_ids:
            if quote_id not in project_quotes:
                self.remove_quote(quote_id)
        self.refresh_infos(quotes_rows)

    def refresh_infos(self, quotes_rows):
        quotes_number = len(quotes_rows)
        self.quotes_number_label.setText(f"You created {quotes_number} quotes")

        means_list = []
        all_votes = []
        for quote_row in quotes_rows:
            votes = json.loads(quote_row['score'])
            if votes == []:
                votes = [0]
            mean = statistics.mean(votes)
            means_list.append(mean)
            all_votes += votes
        if means_list == []:
            means_list = [0]
        all_quotes_mean = round(statistics.mean(means_list), 1)
        self.quote_rank.setText(f"{all_quotes_mean}")
        self.voters_number.setText(f"{len(all_votes)} votes")

class quote_widget(QtWidgets.QFrame):

    delete_signal = pyqtSignal(int)

    def __init__(self, quote_row, parent=None):
        super(quote_widget, self).__init__(parent)
        self.quote_row = quote_row
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def connect_functions(self):
        self.delete_button.clicked.connect(self.delete_quote)

    def delete_quote(self):
        self.delete_signal.emit(self.quote_row['id'])

    def build_ui(self):
        self.setObjectName('user_quote_widget_frame')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.quote_content = QtWidgets.QLabel()
        self.main_layout.addWidget(self.quote_content)

        self.separator = gui_utils.separator()
        self.main_layout.addWidget(self.separator)

        self.rank_widget = QtWidgets.QWidget()
        self.rank_layout = QtWidgets.QHBoxLayout()
        self.rank_layout.setContentsMargins(0,0,0,0)
        self.rank_layout.setSpacing(2)
        self.rank_widget.setLayout(self.rank_layout)
        self.main_layout.addWidget(self.rank_widget)

        self.star_icon = QtWidgets.QLabel()
        self.star_icon.setPixmap(QtGui.QIcon(ressources._star_icon_).pixmap(12))
        self.rank_layout.addWidget(self.star_icon)

        self.quote_rank = QtWidgets.QLabel()
        self.rank_layout.addWidget(self.quote_rank)

        self.quote_max = QtWidgets.QLabel('/5  ')
        self.quote_max.setObjectName('gray_label')
        self.rank_layout.addWidget(self.quote_max)

        self.voters_number = QtWidgets.QLabel()
        self.voters_number.setObjectName('gray_label')
        self.rank_layout.addWidget(self.voters_number)

        self.rank_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.delete_button = QtWidgets.QPushButton()
        self.delete_button.setFixedSize(QtCore.QSize(18,18))
        self.delete_button.setIconSize(QtCore.QSize(12,12))
        self.delete_button.setIcon(QtGui.QIcon(ressources._archive_icon_))
        self.rank_layout.addWidget(self.delete_button)

    def fill_ui(self):
        self.quote_content.setText(self.quote_row['content'])
        rank_list = json.loads(self.quote_row['score'])
        voters_len = len(rank_list)
        if rank_list == []:
            rank_list = [0]
        rank_mean = round(statistics.mean(rank_list), 1)
        self.quote_rank.setText(str(rank_mean))
        self.voters_number.setText(f"{voters_len} votes")
