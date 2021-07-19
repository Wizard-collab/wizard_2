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
        self.stage_id = None
        self.ticket_ids = dict()
        self.build_ui()
        self.connect_functions()
        self.refresh()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_layout.addWidget(self.info_widget)

        self.tickets_scrollArea = QtWidgets.QScrollArea()

        self.tickets_scrollArea_widget = QtWidgets.QWidget()
        self.tickets_scrollArea_widget.setObjectName('tickets_scroll_area')
        self.tickets_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.tickets_scrollArea_layout.setSpacing(0)
        self.tickets_scrollArea_widget.setLayout(self.tickets_scrollArea_layout)

        self.tickets_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.tickets_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tickets_scrollArea.setWidgetResizable(True)
        self.tickets_scrollArea.setWidget(self.tickets_scrollArea_widget)

        self.tickets_widget = QtWidgets.QWidget()
        self.tickets_widget.setObjectName('transparent_widget')
        self.tickets_layout = QtWidgets.QVBoxLayout()
        self.tickets_layout.setSpacing(6)
        self.tickets_layout.setContentsMargins(11,11,11,11)
        self.tickets_widget.setLayout(self.tickets_layout)
        self.tickets_scrollArea_layout.addWidget(self.tickets_widget)

        self.tickets_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.main_layout.addWidget(self.tickets_scrollArea)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setObjectName('dark_widget')
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(8,8,8,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.search_bar = gui_utils.search_bar()
        gui_utils.application_tooltip(self.search_bar, "Search for a specific version")
        self.search_bar.setPlaceholderText('"0023", "user:j.smith", "comment:retake eye"')
        self.buttons_layout.addWidget(self.search_bar)

        self.toggle_visibility_checkBox = QtWidgets.QCheckBox('Only openned tickets')
        self.toggle_visibility_checkBox.setObjectName('transparent_widget')
        self.toggle_visibility_checkBox.setChecked(1)
        self.buttons_layout.addWidget(self.toggle_visibility_checkBox)

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
        self.toggle_visibility_checkBox.stateChanged.connect(self.update_visibility)

    def show_info_mode(self, text, image):
        self.tickets_scrollArea.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.tickets_scrollArea.setVisible(1)

    def refresh(self):
        if self.stage_id is not None:
            tickets_rows = project.get_tickets_by_stage(self.stage_id)
            if tickets_rows is not None:
                if tickets_rows != []:
                    for ticket_row in tickets_rows:
                        if ticket_row['id'] not in self.ticket_ids.keys():
                            new_ticket_widget = ticket_widget(ticket_row)
                            self.ticket_ids[ticket_row['id']] = new_ticket_widget
                            self.tickets_layout.addWidget(new_ticket_widget)
                        else:
                            self.ticket_ids[ticket_row['id']].update(ticket_row)
            self.update_visibility()
        else:
            self.show_info_mode("Select or create a stage\nin the project tree !", ressources._select_stage_info_image_)

    def update_visibility(self):
        if self.toggle_visibility_checkBox.isChecked():
            for ticket_id in self.ticket_ids.keys():
                if self.ticket_ids[ticket_id].ticket_row['state'] == 1:
                    self.ticket_ids[ticket_id].setVisible(1)
                else:
                    self.ticket_ids[ticket_id].setVisible(0)
        else:
            self.show_all()
        self.update_info_mode()

    def update_info_mode(self):
        self.hide_info_mode()
        visible_tickets = []
        for ticket_id in self.ticket_ids.keys():
            if self.ticket_ids[ticket_id].isVisible():
                visible_tickets.append(ticket_id)

        if visible_tickets == []:
            self.show_info_mode("No tickets openned,\nyou're doing it great !", ressources._tickets_info_image_)

    def show_all(self):
        for ticket_id in self.ticket_ids.keys():
            self.ticket_ids[ticket_id].setVisible(1)

    def clear(self):
        self.ticket_ids = dict()
        for i in reversed(range(self.tickets_layout.count())): 
            self.tickets_layout.itemAt(i).widget().setParent(None)

    def change_stage(self, stage_id):
        self.stage_id = stage_id
        self.clear()
        self.refresh()
        self.info_widget.pop()

class ticket_widget(QtWidgets.QWidget):
    def __init__(self, ticket_row, parent = None):
        super(ticket_widget, self).__init__(parent)
        self.ticket_row = ticket_row
        self.build_ui()
        self.connect_functions()
        self.fill_ui()

    def update(self, ticket_row):
        self.ticket_row = ticket_row
        self.refresh()

    def refresh(self):
        if self.ticket_row['state'] == 1:
            state = 'Open'
            color = '#edaa6b'
            self.close_ticket_button.setObjectName('red_button')
            self.close_ticket_button.setStyleSheet('''
                                                    #red_button{
                                                        border: 2px solid #f0605b;
                                                    }

                                                    #red_button::hover{
                                                        background-color: #ff817d;
                                                        border: 2px solid #ff817d;
                                                    }

                                                    #red_button::pressed{
                                                        background-color: #ab4946;
                                                        border: 2px solid #ab4946;
                                                    }''')
            self.close_ticket_button.setText('Close')
        else:
            state = 'Closed'
            color = '#8fcc70'
            self.close_ticket_button.setObjectName('blue_button')
            self.close_ticket_button.setStyleSheet('''
                                                    #blue_button{
                                                        background-color: transparent;
                                                        border: 2px solid #7785de;
                                                    }

                                                    #blue_button::hover{
                                                        background-color: #8e9dfa;
                                                        border: 2px solid #8e9dfa;
                                                    }

                                                    #blue_button::pressed{
                                                        background-color: #6772b5;
                                                        border: 2px solid #6772b5;
                                                    }''')
            self.close_ticket_button.setText('Open')

        self.state_label.setStyleSheet('color:%s'%color)
        self.state_label.setText(state)

    def fill_ui(self):
        self.title_label.setText(self.ticket_row['title'])
        self.user_name_label.setText(self.ticket_row['creation_user'])
        if self.ticket_row['destination_user'] is None:
            destination_user = 'everybody'
        else:
            destination_user = self.ticket_row['destination_user']
        self.destination_label.setText(destination_user)
        day, hour = tools.convert_time(self.ticket_row['creation_time'])
        self.date_label.setText(f"{day} - {hour}")
        profile_picture = site.get_user_row_by_name(self.ticket_row['creation_user'], 'profile_picture')
        gui_utils.round_image(self.profile_picture, image.convert_str_data_to_image_bytes(profile_picture), 50)
        self.content_label.setText(self.ticket_row['message'])

        files_list = json.loads(self.ticket_row['files'])
        for file in files_list:
            new_file_button = file_button(file)
            #new_file_button.clicked.connect(lambda: self.open_file(new_file_button.file))
            self.files_scrollArea_layout.insertWidget(0,new_file_button)
        if len(files_list)>=1:
            self.files_scrollArea.setVisible(True)
        self.refresh()

    def open_file(self, file):
        os.startfile(file)

    def toggle_ticket(self):
        if self.ticket_row['state'] == 1:
            assets.close_ticket(self.ticket_row['id'])
        else:
            assets.open_ticket(self.ticket_row['id'])

    def connect_functions(self):
        self.close_ticket_button.clicked.connect(self.toggle_ticket)

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
        self.user_infos_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

        self.title_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding))

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(50,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

        self.close_ticket_button = QtWidgets.QPushButton('Close')
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
        self.clicked.connect(self.open)

    def open(self):
        os.startfile(self.file)
