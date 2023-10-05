# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import artefact_interaction_widget

# Wizard modules
from wizard.core import repository
from wizard.core import environment
from wizard.core import artefacts
from wizard.vars import ressources
from wizard.vars import game_vars

class inventory_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(inventory_widget, self).__init__(parent)
        self.artefacts = dict()
        self.artefact_interaction_widget = artefact_interaction_widget.artefact_interaction_widget()
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.coins_widget.give_coins_signal.connect(self.give_coins)

    def build_ui(self):
        self.setObjectName('dark_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.artefacts_view = QtWidgets.QListView()
        self.artefacts_view = QtWidgets.QListWidget()
        self.artefacts_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.artefacts_view.setObjectName('market_icon_view')
        self.artefacts_view.setSpacing(4)
        self.artefacts_view.setMovement(QtWidgets.QListView.Static)
        self.artefacts_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.artefacts_view.setViewMode(QtWidgets.QListView.IconMode)
        self.artefacts_view.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.artefacts_view_scrollBar = self.artefacts_view.verticalScrollBar()
        self.main_layout.addWidget(self.artefacts_view)

        self.coins_item = QtWidgets.QListWidgetItem('')
        self.coins_widget = coins_item()
        self.artefacts_view.addItem(self.coins_item)
        self.artefacts_view.setItemWidget(self.coins_item, self.coins_widget)
        self.coins_item.setSizeHint(self.coins_widget.size())

    def refresh(self):
        if not self.isVisible():
            return
        self.coins_widget.refresh()
        self.artefact_interaction_widget.refresh()
        user_row = repository.get_user_row_by_name(environment.get_user())
        artefacts_list = json.loads(user_row['artefacts'])
        artefacts_set = list(set(artefacts_list))
        for artefact in artefacts_set:
            if artefact not in self.artefacts.keys():
                artefact_list_item = QtWidgets.QListWidgetItem('')
                artefact_widget = artefact_item(artefact)
                artefact_widget.use_artefact_signal.connect(self.use_artefact)
                artefact_widget.give_artefact_signal.connect(self.give_artefact)
                self.artefacts_view.addItem(artefact_list_item)
                artefact_list_item.setSizeHint(artefact_widget.size())
                self.artefacts_view.setItemWidget(artefact_list_item, artefact_widget)
                self.artefacts[artefact] = dict()
                self.artefacts[artefact]['item'] = artefact_list_item
                self.artefacts[artefact]['widget'] = artefact_widget
            self.artefacts[artefact]['widget'].update_number(artefacts_list.count(artefact))
        existing_artefact_list = list(self.artefacts)
        for artefact in existing_artefact_list:
            if artefact not in artefacts_list:
                self.remove_item(artefact)

    def use_artefact(self, artefact):
        if game_vars.artefacts_dic[artefact]['type'] == 'attack':
            if self.artefact_interaction_widget.exec_() == QtWidgets.QDialog.Accepted:
                user = self.artefact_interaction_widget.user
            else:
                return
        else:
            user = environment.get_user()
        if not artefacts.use_artefact(artefact, user):
            return
        gui_server.refresh_ui()
        gui_server.custom_popup(f"Inventory", f"You just used {game_vars.artefacts_dic[artefact]['name']} on {user}", ressources._purse_icon_)

    def give_artefact(self, artefact):
        if self.artefact_interaction_widget.exec_() != QtWidgets.QDialog.Accepted:
            return
        user = self.artefact_interaction_widget.user
        artefacts.give_artefact(artefact, user)
        gui_server.refresh_team_ui()
        gui_server.custom_popup(f"Inventory", f"You just gived {game_vars.artefacts_dic[artefact]['name']} to {user}", ressources._purse_icon_)

    def give_coins(self):
        if self.artefact_interaction_widget.exec_() != QtWidgets.QDialog.Accepted:
            return
        self.give_coins_widget = give_coins_widget()
        if self.give_coins_widget.exec_() != QtWidgets.QDialog.Accepted:
            return
        amount = self.give_coins_widget.amount_field.value()
        user = self.artefact_interaction_widget.user
        artefacts.give_coins(amount, user)
        gui_server.refresh_team_ui()
        gui_server.custom_popup(f"Inventory", f"You just gived {amount} coins to {user}", ressources._purse_icon_)

    def remove_item(self, artefact):
        if artefact not in self.artefacts.keys():
            return
        item = self.artefacts[artefact]['item']
        widget = self.artefacts[artefact]['widget']
        widget.setParent(None)
        widget.deleteLater()
        self.artefacts_view.takeItem(self.artefacts_view.row(item))
        del self.artefacts[artefact]

class coins_item(QtWidgets.QFrame):

    give_coins_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(coins_item, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def refresh(self):
        coins = repository.get_user_row_by_name(environment.get_user(), 'coins')
        self.number_label.setText(f"x{coins}")

    def build_ui(self):
        self.setFixedSize(250, 130)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.artefact_icon = QtWidgets.QLabel()
        self.artefact_icon.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.artefact_icon.setPixmap(QtGui.QIcon(ressources._coin_icon_).pixmap(70))
        self.main_layout.addWidget(self.artefact_icon)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(2)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.artefact_name = QtWidgets.QLabel('Coins')
        self.artefact_name.setObjectName('title_label_2')
        self.content_layout.addWidget(self.artefact_name)

        self.info_label = QtWidgets.QLabel("Your coins")
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('gray_label')
        self.content_layout.addWidget(self.info_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0,0,0,0)
        self.button_layout.setSpacing(2)
        self.content_layout.addLayout(self.button_layout)

        self.number_label = QtWidgets.QLabel()
        self.number_label.setObjectName('title_label_2')
        self.number_label.setStyleSheet('color:#f2c96b')
        self.button_layout.addWidget(self.number_label)

        self.button_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.give_button = QtWidgets.QPushButton(f"Give")
        self.give_button.setStyleSheet('padding:2px')
        self.give_button.setIcon(QtGui.QIcon(ressources._purse_icon_))
        self.give_button.setIconSize(QtCore.QSize(18,18))
        self.button_layout.addWidget(self.give_button)

    def connect_functions(self):
        self.give_button.clicked.connect(self.give_coins)

    def give_coins(self):
        self.give_coins_signal.emit('')

class artefact_item(QtWidgets.QFrame):

    use_artefact_signal = pyqtSignal(str)
    give_artefact_signal = pyqtSignal(str)

    def __init__(self, artefact, parent=None):
        super(artefact_item, self).__init__(parent)
        self.artefact = artefact
        self.artefact_dic = game_vars.artefacts_dic[artefact]
        self.number = 0
        self.build_ui()
        self.connect_functions()

    def update_number(self, number):
        self.number = number
        self.fill_ui()

    def fill_ui(self):
        self.number_label.setText(f"x{self.number}")

    def build_ui(self):
        icon = QtGui.QIcon(self.artefact_dic['icon'])
        self.setFixedSize(250, 130)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setObjectName('round_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)

        self.artefact_icon = QtWidgets.QLabel()
        self.artefact_icon.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.artefact_icon.setPixmap(icon.pixmap(70))
        self.main_layout.addWidget(self.artefact_icon)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(2)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.artefact_name = QtWidgets.QLabel(self.artefact_dic['name'])
        self.artefact_name.setObjectName('title_label_2')
        self.content_layout.addWidget(self.artefact_name)

        self.info_label = QtWidgets.QLabel(self.artefact_dic['description'])
        self.info_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.info_label.setWordWrap(True)
        self.info_label.setObjectName('gray_label')
        self.content_layout.addWidget(self.info_label)

        self.type_label = QtWidgets.QLabel(self.artefact_dic['type'].capitalize())
        self.type_label.setStyleSheet('color:#f2c96b')
        self.type_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_layout.addWidget(self.type_label)

        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.setContentsMargins(0,0,0,0)
        self.button_layout.setSpacing(2)
        self.content_layout.addLayout(self.button_layout)

        self.number_label = QtWidgets.QLabel()
        self.number_label.setObjectName('title_label_2')
        self.number_label.setStyleSheet('color:#f2c96b')
        self.button_layout.addWidget(self.number_label)

        self.button_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.give_button = QtWidgets.QPushButton(f"Give")
        self.give_button.setStyleSheet('padding:2px')
        self.give_button.setIcon(QtGui.QIcon(ressources._purse_icon_))
        self.give_button.setIconSize(QtCore.QSize(18,18))
        self.button_layout.addWidget(self.give_button)

        self.use_button = QtWidgets.QPushButton(f"Use")
        self.use_button.setStyleSheet('padding:2px')
        self.use_button.setIcon(icon)
        self.use_button.setIconSize(QtCore.QSize(18,18))
        self.button_layout.addWidget(self.use_button)

    def connect_functions(self):
        self.use_button.clicked.connect(self.use_artefact)
        self.give_button.clicked.connect(self.give_artefact)

    def use_artefact(self):
        self.use_artefact_signal.emit(self.artefact)

    def give_artefact(self):
        self.give_artefact_signal.emit(self.artefact)
        
class give_coins_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(give_coins_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        corner = gui_utils.move_ui(self)
        self.apply_round_corners(corner)
        event.accept()
        self.amount_field.setFocus()

    def apply_round_corners(self, corner):
        self.main_frame.setStyleSheet("#variant_creation_widget{border-%s-radius:0px;}"%corner)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(8,8,8,8)
        self.setLayout(self.main_layout)

        self.main_frame = QtWidgets.QFrame()
        self.main_frame.setObjectName('instance_creation_frame')
        self.frame_layout = QtWidgets.QVBoxLayout()
        self.frame_layout.setSpacing(6)
        self.main_frame.setLayout(self.frame_layout)
        self.main_layout.addWidget(self.main_frame)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_frame.setGraphicsEffect(self.shadow)

        self.close_frame = QtWidgets.QFrame()
        self.close_layout = QtWidgets.QHBoxLayout()
        self.close_layout.setContentsMargins(2,2,2,2)
        self.close_layout.setSpacing(2)
        self.close_frame.setLayout(self.close_layout)
        self.close_layout.addWidget(QtWidgets.QLabel('Coin amount to give'))
        self.spaceItem = QtWidgets.QSpacerItem(100,10,QtWidgets.QSizePolicy.Expanding)
        self.close_layout.addSpacerItem(self.spaceItem)
        self.close_pushButton = gui_utils.transparent_button(ressources._close_tranparent_icon_, ressources._close_icon_)
        self.close_pushButton.setFixedSize(16,16)
        self.close_pushButton.setIconSize(QtCore.QSize(12,12))
        self.close_layout.addWidget(self.close_pushButton)
        self.frame_layout.addWidget(self.close_frame)

        self.amount_field = QtWidgets.QSpinBox()
        self.amount_field.setRange(1, 2147483647)
        self.amount_field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.frame_layout.addWidget(self.amount_field)

        self.accept_button = QtWidgets.QPushButton('Give')
        self.accept_button.setObjectName("blue_button")
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.frame_layout.addWidget(self.accept_button)

    def connect_functions(self):
        self.accept_button.clicked.connect(self.accept)
        self.close_pushButton.clicked.connect(self.reject)