# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.core import project
from wizard.core import image
from wizard.core import tools

# Wizard gui modules
from wizard.gui import gui_utils

class ticket_widget(QtWidgets.QWidget):
    def __init__(self, ticket_id, parent = None):
        super(ticket_widget, self).__init__(parent)
        self.ticket_id = ticket_id
        self.build_ui()
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

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

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
        self.title_widget.setObjectName('ticket_header_frame')
        self.title_layout = QtWidgets.QVBoxLayout()
        self.title_layout.setContentsMargins(0,0,0,0)
        self.title_layout.setSpacing(2)
        self.title_widget.setLayout(self.title_layout)
        self.header_layout.addWidget(self.title_widget)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.title_label = QtWidgets.QLabel('Title')
        self.title_label.setObjectName('title_label')
        self.title_layout.addWidget(self.title_label)

        self.user_infos_widget = QtWidgets.QFrame()
        self.user_infos_widget.setObjectName('ticket_header_frame')
        self.user_infos_layout = QtWidgets.QHBoxLayout()
        self.user_infos_layout.setContentsMargins(0,0,0,0)
        self.user_infos_layout.setSpacing(6)
        self.user_infos_widget.setLayout(self.user_infos_layout)
        self.title_layout.addWidget(self.user_infos_widget)

        self.user_name_label = QtWidgets.QLabel('l.brunel')
        self.user_infos_layout.addWidget(self.user_name_label)

        self.arrow_label = QtWidgets.QLabel('>')
        self.arrow_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.arrow_label)

        self.destination_label = QtWidgets.QLabel('everybody')
        self.user_infos_layout.addWidget(self.destination_label)

        self.edge_label = QtWidgets.QLabel('-')
        self.edge_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.edge_label)

        self.date_label = QtWidgets.QLabel('23/06/1995 - 23:54')
        self.date_label.setObjectName('gray_label')
        self.user_infos_layout.addWidget(self.date_label)

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(50,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

        self.close_ticket_button = QtWidgets.QPushButton('Close')
        self.close_ticket_button.setObjectName('red_button')
        self.header_layout.addWidget(self.close_ticket_button)

        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QHBoxLayout()
        self.content_layout.setContentsMargins(11,11,11,11)
        self.content_layout.setSpacing(6)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        self.content_label = QtWidgets.QLabel('zoeifj ozeifj zeoifj eziofj zf')
        self.content_layout.addWidget(self.content_label)

