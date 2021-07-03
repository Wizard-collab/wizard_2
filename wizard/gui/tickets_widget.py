# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
import os   
import json 

# Wizard modules
from wizard.core import site
from wizard.core import project
from wizard.core import assets
from wizard.core import image
from wizard.core import tools
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_utils

class tickets_widget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(tickets_widget, self).__init__(parent)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.tickets_scrollArea = QtWidgets.QScrollArea()

        self.tickets_scrollArea_widget = QtWidgets.QWidget()
        self.tickets_scrollArea_widget.setObjectName('tickets_scroll_area')
        self.tickets_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.tickets_scrollArea_layout.setSpacing(6)
        self.tickets_scrollArea_widget.setLayout(self.tickets_scrollArea_layout)

        self.tickets_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tickets_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tickets_scrollArea.setWidgetResizable(True)
        self.tickets_scrollArea.setWidget(self.tickets_scrollArea_widget)

        self.main_layout.addWidget(self.tickets_scrollArea)

    def refresh(self):
        self.all_tickets_ids = project.get_all_tickets('id')
        for ticket_id in self.all_tickets_ids:
            new_ticket_widget = ticket_widget(ticket_id)
            self.tickets_scrollArea_layout.addWidget(new_ticket_widget)

class ticket_widget(QtWidgets.QWidget):
    def __init__(self, ticket_id, parent = None):
        super(ticket_widget, self).__init__(parent)
        self.ticket_id = ticket_id
        self.build_ui()
        self.connect_functions()
        self.fill_ui()

    def fill_ui(self):
        ticket_row = project.get_ticket_data(self.ticket_id)
        self.title_label.setText(ticket_row['title'])
        self.user_name_label.setText(ticket_row['creation_user'])
        if ticket_row['destination_user'] is None:
            destination_user = 'everybody'
        else:
            destination_user = ticket_row['destination_user']
        self.destination_label.setText(destination_user)
        day, hour = tools.convert_time(ticket_row['creation_time'])
        self.date_label.setText(f"{day} - {hour}")
        profile_picture = site.get_user_row_by_name(ticket_row['creation_user'], 'profile_picture')
        gui_utils.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(profile_picture), 50)
        self.content_label.setText(ticket_row['message'])

        if ticket_row['state'] == 1:
            state = 'Open'
            color = '#edaa6b'
        else:
            state = 'Closed'
            color = '#8fcc70'
            self.close_ticket_button.setObjectName('blue_button')
            self.close_ticket_button.setText('Open')
            self.close_ticket_button.clicked.disconnect(self.close_ticket)
            self.close_ticket_button.clicked.connect(self.open_ticket)

        self.state_label.setStyleSheet('color:%s'%color)
        self.state_label.setText(state)

        files_list = json.loads(ticket_row['files'])
        for file in files_list:
            new_file_button = file_button(file)
            new_file_button.clicked.connect(lambda: self.open_file(new_file_button.file))
            self.files_scrollArea_layout.insertWidget(0,new_file_button)
        if len(files_list)>=1:
            self.files_scrollArea.setVisible(True)

    def open_file(self, file):
        os.startfile(file)

    def close_ticket(self):
        assets.close_ticket(self.ticket_id)

    def open_ticket(self):
        assets.open_ticket(self.ticket_id)

    def connect_functions(self):
        self.close_ticket_button.clicked.connect(self.close_ticket)

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)
        self.setObjectName('ticket_widget')

        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.header_frame.setObjectName('ticket_header_frame')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(11,11,11,11)
        self.header_layout.setSpacing(6)
        self.header_frame.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_frame)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(50,50)
        self.header_layout.addWidget(self.profile_picture)

        self.title_widget = QtWidgets.QFrame()
        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.title_widget.setLayout(self.title_layout)
        self.header_layout.addWidget(self.title_widget)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName('title_label')
        self.title_layout.addWidget(self.title_label)

        self.user_infos_widget = QtWidgets.QFrame()
        self.user_infos_layout = QtWidgets.QHBoxLayout()
        self.user_infos_layout.setContentsMargins(0,0,0,0)
        self.user_infos_layout.setSpacing(6)
        self.user_infos_widget.setLayout(self.user_infos_layout)
        self.title_layout.addWidget(self.user_infos_widget)

        self.user_name_label = QtWidgets.QLabel()
        self.user_infos_layout.addWidget(self.user_name_label)

        self.arrow_label = QtWidgets.QLabel('>')
        self.arrow_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.arrow_label)

        self.destination_label = QtWidgets.QLabel()
        self.user_infos_layout.addWidget(self.destination_label)

        self.edge_label = QtWidgets.QLabel('-')
        self.edge_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.edge_label)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.date_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(50,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

        self.close_ticket_button = QtWidgets.QPushButton('Close')
        self.close_ticket_button.setObjectName('red_button')
        self.header_layout.addWidget(self.close_ticket_button)

        self.content_widget = QtWidgets.QWidget()
        self.content_widget.setObjectName('ticket_content_widget')
        self.content_layout = QtWidgets.QVBoxLayout()
        self.content_layout.setContentsMargins(20,20,20,20)
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.content_label = QtWidgets.QLabel()
        self.content_label.setWordWrap(True)
        self.content_layout.addWidget(self.content_label)

        self.files_scrollArea = QtWidgets.QScrollArea()
        self.files_scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.files_scrollArea.setVisible(False)
        self.files_scrollArea_widget = QtWidgets.QWidget()
        self.files_scrollArea_layout = QtWidgets.QHBoxLayout()
        self.files_scrollArea_layout.setSpacing(6)
        self.files_scrollArea_layout.setContentsMargins(0,0,0,0)
        self.files_scrollArea_widget.setLayout(self.files_scrollArea_layout)
        self.files_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.files_scrollArea.setWidgetResizable(True)
        self.files_scrollArea.setWidget(self.files_scrollArea_widget)
        self.content_layout.addWidget(self.files_scrollArea)

        self.files_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))
        self.content_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.content_infos_widget = QtWidgets.QWidget()
        self.content_infos_layout = QtWidgets.QHBoxLayout()
        self.content_infos_layout.setContentsMargins(0,0,0,0)
        self.content_infos_layout.setSpacing(6)
        self.content_infos_widget.setLayout(self.content_infos_layout)
        self.content_layout.addWidget(self.content_infos_widget)
        self.content_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(50,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

        self.state_info_label = QtWidgets.QLabel('state')
        self.state_info_label.setObjectName('gray_label')
        self.content_infos_layout.addWidget(self.state_info_label)

        self.state_label = QtWidgets.QLabel()
        self.state_label.setObjectName('bold_label')
        self.content_infos_layout.addWidget(self.state_label)

class file_button(QtWidgets.QPushButton):
    def __init__(self, file, parent=None):
        super(file_button, self).__init__(parent)
        self.file = file
        self.build_ui()

    def build_ui(self):
        self.setObjectName('file_button')
        self.setIcon(QtGui.QIcon(ressources._file_icon_))
        self.setText(os.path.basename(self.file))
