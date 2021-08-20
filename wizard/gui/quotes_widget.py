# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import random
import json
import statistics

# Wizard modules
from wizard.core import site
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import create_quote_widget

class quotes_widget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(quotes_widget, self).__init__(parent)
        self.previous_quote_id = None
        self.timer=QtCore.QTimer(self)
        self.build_ui()
        self.connect_functions()
        self.get_new_random_quote(without_anim=1)
        self.start_timer()

    def build_ui(self):
        self.setObjectName('transparent_widget')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.animation_handler_widget = QtWidgets.QWidget()
        self.animation_handler_widget.setObjectName('transparent_widget')
        self.animation_handler_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        self.animation_handler_layout = QtWidgets.QHBoxLayout()
        self.animation_handler_layout.setContentsMargins(0,0,0,0)
        self.animation_handler_layout.setSpacing(6)
        self.animation_handler_widget.setLayout(self.animation_handler_layout)
        self.main_layout.addWidget(self.animation_handler_widget)

        self.animation_handler_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.quote_label = gui_utils.ElidedLabel()
        self.quote_label.setAlignment(QtCore.Qt.AlignCenter)
        self.quote_label.setObjectName('quote_label')
        self.quote_label.setMinimumHeight(0)
        self.animation_handler_layout.addWidget(self.quote_label)

        self.score_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.score_slider.setRange(0,5)
        self.score_slider.setFixedWidth(60)
        self.animation_handler_layout.addWidget(self.score_slider)
        
        self.random_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.random_button, "Show new random quote")
        self.random_button.setIcon(QtGui.QIcon(ressources._random_icon_))
        self.random_button.setIconSize(QtCore.QSize(16,16))
        self.random_button.setFixedSize(20,20)
        self.animation_handler_layout.addWidget(self.random_button)

        self.add_button = QtWidgets.QPushButton()
        gui_utils.application_tooltip(self.add_button, "Create new quote")
        self.add_button.setIcon(QtGui.QIcon(ressources._add_icon_))
        self.add_button.setIconSize(QtCore.QSize(14,14))
        self.add_button.setFixedSize(20,20)
        self.animation_handler_layout.addWidget(self.add_button)

        self.animation_handler_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

    def connect_functions(self):
        self.timer.timeout.connect(self.clear_anim)
        self.random_button.clicked.connect(self.clear_anim)
        self.random_button.clicked.connect(self.timer.stop)
        self.score_slider.sliderReleased.connect(self.vote)
        self.add_button.clicked.connect(self.add_quote)

    def add_quote(self):
        self.create_quote_widget = create_quote_widget.create_quote_widget(self)
        self.create_quote_widget.exec_()

    def vote(self):
        score = self.score_slider.value()
        site.add_quote_score(self.quote_row['id'], score)

    def get_new_random_quote(self, without_anim=0):
        self.animation_handler_widget.setVisible(0)
        QtWidgets.QApplication.processEvents()
        quotes_ids = site.get_all_quotes('id')
        self.random_index = random.randint(0, len(quotes_ids)-1)
        while self.random_index == self.previous_quote_id:
            self.random_index = random.randint(0, len(quotes_ids)-1)
        self.previous_quote_id = self.random_index
        self.quote_row = site.get_quote_data(quotes_ids[self.random_index])
        content = self.quote_row['content']
        content = content.replace('\n', ' ')
        content = content.replace('\r\n', ' ')
        content = content.replace('\r', ' ')
        self.quote_label.setText(content)
        self.update_score_slider()
        if not without_anim:
            self.new_anim()
        QtWidgets.QApplication.processEvents()
        self.animation_handler_widget.setVisible(1)
        self.start_timer()

    def update_score_slider(self):
        score_list = json.loads(self.quote_row['score'])
        if score_list != []:
            self.score_slider.setValue(int(statistics.mean(score_list)))
        else:
            self.score_slider.setValue(0)

    def clear_anim(self):
        self.animation = QtCore.QPropertyAnimation(self.animation_handler_widget, b"geometry")
        self.animation.setDuration(200);
        self.animation.setStartValue(QtCore.QRect(self.geometry().x()-150, self.geometry().y(), self.geometry().width(), self.geometry().height()))
        self.animation.setEndValue(QtCore.QRect(self.geometry().x()-150, 50, self.geometry().width(), self.geometry().height()))
        self.animation.finished.connect(self.get_new_random_quote)
        self.animation.start()

    def new_anim(self):
        self.animation = QtCore.QPropertyAnimation(self.animation_handler_widget, b"geometry")
        self.animation.setDuration(400)
        self.animation.setStartValue(QtCore.QRect(self.geometry().x()-150, -50, self.geometry().width(), self.geometry().height()))
        self.animation.setEndValue(QtCore.QRect(self.geometry().x()-150, self.geometry().y(), self.geometry().width(), self.geometry().height()))
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutBounce)
        self.animation.start()

    def start_timer(self):
        self.timer.start(30000)


