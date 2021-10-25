# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import json
import os

# Wizard modules
from wizard.vars import ressources
from wizard.core import tools
from wizard.core import image
from wizard.core import site
from wizard.core import assets
from wizard.core import project

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server
from wizard.gui import drop_files_widget

class ticket_history_widget(QtWidgets.QWidget):

    toggle_ticket_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(ticket_history_widget, self).__init__(parent)
        self.parent = parent
        self.ticket_id = None
        self.ticket_messages_ids = dict()
        self.build_ui()
        self.connect_functions()

    def showEvent(self, event):
        self.set_geometry()
        event.accept()

    def set_geometry(self):
        parent_x = self.parent.x()
        parent_y = self.parent.y()
        parent_width = self.parent.width()
        parent_height = self.parent.height()
        pos_x = (parent_x + parent_width)-self.width()
        pos_y = (parent_y)
        self.setGeometry(pos_x, pos_y, self.width(), parent_height)

    def build_ui(self):
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12,12,12,12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setMinimumWidth(500)
        self.main_widget.setObjectName('round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12,12,12,12)
        self.main_layout.setSpacing(12)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.main_widget.setGraphicsEffect(self.shadow)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('transparent_widget')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.messages_icon = QtWidgets.QLabel('')
        self.messages_icon.setPixmap(QtGui.QIcon(ressources._messages_icon_).pixmap(32))
        self.messages_icon.setFixedSize(32,32)
        self.header_layout.addWidget(self.messages_icon)

        self.thread_label = QtWidgets.QLabel('Thread - ')
        self.thread_label.setObjectName('title_label')
        self.header_layout.addWidget(self.thread_label)

        self.status_label = QtWidgets.QLabel()
        self.status_label.setObjectName('title_label')
        self.header_layout.addWidget(self.status_label)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.toggle_ticket_button = QtWidgets.QPushButton('Close ticket')
        self.toggle_ticket_button.setObjectName('blue_button')
        self.toggle_ticket_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.header_layout.addWidget(self.toggle_ticket_button)

        self.ticket_messages_scrollArea = QtWidgets.QScrollArea()
        self.ticket_messages_scrollBar = self.ticket_messages_scrollArea.verticalScrollBar()

        self.ticket_messages_scrollArea_widget = QtWidgets.QWidget()
        self.ticket_messages_scrollArea_widget.setObjectName('wall_scroll_area')
        self.ticket_messages_scrollArea_layout = QtWidgets.QVBoxLayout()
        self.ticket_messages_scrollArea_layout.setContentsMargins(2,2,2,2)
        self.ticket_messages_scrollArea_layout.setSpacing(2)
        self.ticket_messages_scrollArea_widget.setLayout(self.ticket_messages_scrollArea_layout)

        #self.ticket_messages_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.ticket_messages_scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.ticket_messages_scrollArea.setWidgetResizable(True)
        self.ticket_messages_scrollArea.setWidget(self.ticket_messages_scrollArea_widget)
        self.ticket_messages_scrollBar = self.ticket_messages_scrollArea.verticalScrollBar()
        self.ticket_messages_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        self.messages_widget = QtWidgets.QWidget()
        self.messages_widget.setObjectName('transparent_widget')
        self.messages_layout = QtWidgets.QVBoxLayout()
        self.messages_layout.setContentsMargins(0,0,0,0)
        self.messages_layout.setSpacing(2)
        self.messages_widget.setLayout(self.messages_layout)

        self.ticket_messages_scrollArea_layout.addWidget(self.messages_widget)
        self.post_widget = post_widget()
        self.ticket_messages_scrollArea_layout.addWidget(self.post_widget)

        self.main_layout.addWidget(self.ticket_messages_scrollArea)

    def connect_functions(self):
        self.post_widget.post_signal.connect(self.post)
        self.ticket_messages_scrollBar.rangeChanged.connect(lambda: self.ticket_messages_scrollBar.setValue(self.ticket_messages_scrollBar.maximum()))
        self.toggle_ticket_button.clicked.connect(self.toggle_ticket_signal.emit)

    def post(self):
        self.post_widget.post(self.ticket_id)

    def change_ticket(self, ticket_id):
        self.clear()
        self.post_widget.clear()
        self.ticket_id = ticket_id
        self.refresh()
        if self.ticket_id is None:
            self.hide()
        else:
            self.setVisible(1)

    def clear(self):
        self.ticket_messages_ids = dict()
        for i in reversed(range(self.messages_layout.count())): 
            self.messages_layout.itemAt(i).widget().setParent(None)

    def refresh_header(self):
        if self.ticket_id is not None:
            ticket_state = project.get_ticket_data(self.ticket_id, 'state')
            if ticket_state == 1:
                self.status_label.setText('Open')
                self.status_label.setStyleSheet("color:#f0605b;")

                self.toggle_ticket_button.setText('Close ticket')
                self.toggle_ticket_button.setObjectName('green_button')
                self.toggle_ticket_button.setStyleSheet('''
                                                        #green_button{
                                                            background-color: transparent;
                                                            border: 2px solid #9cf277;
                                                        }

                                                        #green_button::hover{
                                                            background-color: #9cf277;
                                                            border: 2px solid #9cf277;
                                                        }

                                                        #green_button::pressed{
                                                            background-color: #7bbe5e;
                                                            border: 2px solid #7bbe5e;
                                                        }''')

            elif ticket_state == 0:
                self.status_label.setText('Closed')
                self.status_label.setStyleSheet("color:#9cf277;")

                self.toggle_ticket_button.setText('Open ticket')
                self.toggle_ticket_button.setObjectName('red_button')
                self.toggle_ticket_button.setStyleSheet('''
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

            else:
                self.status_label.setText('')
                self.status_label.setStyleSheet("")
        else:
            self.status_label.setText('')
            self.status_label.setStyleSheet("")

    def refresh(self):
        self.refresh_header()
        if self.ticket_id is not None:
            ticket_messages_rows = project.get_ticket_messages(self.ticket_id)
            if ticket_messages_rows is not None:
                for ticket_message_row in ticket_messages_rows:
                    if ticket_message_row['id'] not in self.ticket_messages_ids.keys():
                        widget = ticket_message_widget(ticket_message_row)
                        self.messages_layout.addWidget(widget)
                        self.ticket_messages_ids[ticket_message_row['id']] = widget

class ticket_message_widget(QtWidgets.QFrame):
    def __init__(self, ticket_message_row, parent = None):
        super(ticket_message_widget, self).__init__(parent)
        self.ticket_message_row = ticket_message_row
        self.build_ui()
        self.refresh()

    def build_ui(self):
        self.setObjectName('ticket_message_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_widget.setObjectName('ticket_message_header_frame')
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setAlignment(QtCore.Qt.AlignTop)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.profile_picture_widget = QtWidgets.QWidget()
        self.profile_picture_widget.setObjectName('transparent_widget')
        self.profile_picture_widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.profile_picture_layout = QtWidgets.QVBoxLayout()
        self.profile_picture_layout.setAlignment(QtCore.Qt.AlignTop)
        self.profile_picture_layout.setContentsMargins(0,0,0,0)
        self.profile_picture_layout.setSpacing(0)
        self.profile_picture_widget.setLayout(self.profile_picture_layout)
        self.header_layout.addWidget(self.profile_picture_widget)

        self.profile_picture = QtWidgets.QLabel()
        self.profile_picture.setFixedSize(40,40)
        self.profile_picture_layout.addWidget(self.profile_picture)

        self.infos_widget = QtWidgets.QWidget()
        self.infos_widget.setObjectName('transparent_widget')
        self.infos_layout = QtWidgets.QVBoxLayout()
        self.infos_layout.setContentsMargins(0,0,0,0)
        self.infos_layout.setSpacing(8)
        self.infos_widget.setLayout(self.infos_layout)
        self.header_layout.addWidget(self.infos_widget)


        self.user_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.user_label)

        self.date_label = QtWidgets.QLabel()
        self.date_label.setObjectName('gray_label')
        self.infos_layout.addWidget(self.date_label)

        self.message_label = QtWidgets.QLabel()
        self.infos_layout.addWidget(self.message_label)

        self.files_scrollArea = QtWidgets.QScrollArea()
        self.files_scrollArea.setObjectName('ticket_message_widget')
        self.files_scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.files_scrollArea.setVisible(False)
        self.files_scrollArea_widget = QtWidgets.QWidget()
        self.files_scrollArea_widget.setObjectName('transparent_widget')
        self.files_scrollArea_layout = QtWidgets.QHBoxLayout()
        self.files_scrollArea_layout.setSpacing(6)
        self.files_scrollArea_layout.setContentsMargins(0,0,0,0)
        self.files_scrollArea_widget.setLayout(self.files_scrollArea_layout)
        self.files_scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.files_scrollArea.setWidgetResizable(True)
        self.files_scrollArea.setWidget(self.files_scrollArea_widget)
        self.infos_layout.addWidget(self.files_scrollArea)

        self.files_scrollArea_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))

    def refresh(self):
        profile_image = site.get_user_row_by_name(self.ticket_message_row['creation_user'], 'profile_picture')
        pm = gui_utils.mask_image(image.convert_str_data_to_image_bytes(profile_image), 'png', 40)
        self.profile_picture.setPixmap(pm)
        self.user_label.setText(self.ticket_message_row['creation_user'])
        day, hour = tools.convert_time(self.ticket_message_row['creation_time'])
        self.date_label.setText(f"{day} - {hour}")
        self.message_label.setText(self.ticket_message_row['message'])

        files_list = json.loads(self.ticket_message_row['files'])
        for file in files_list:
            new_file_button = file_button(file)
            self.files_scrollArea_layout.insertWidget(0,new_file_button)
        if len(files_list)>=1:
            self.files_scrollArea.setVisible(True)

class file_button(QtWidgets.QPushButton):
    def __init__(self, file, parent=None):
        super(file_button, self).__init__(parent)
        self.file = file
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('file_button')

    def fill_ui(self):
        lowered_file = self.file.lower()
        if lowered_file.endswith('.png') or lowered_file.endswith('.jpg'):
            self.setIcon(QtGui.QIcon(self.file))
            self.setIconSize(QtCore.QSize(100,100))
            self.setText('')
        else:
            self.setIcon(QtGui.QIcon(ressources._file_icon_))
            self.setText(os.path.basename(self.file))

    def connect_functions(self):
        self.clicked.connect(self.open)

    def open(self):
        os.startfile(self.file)
        
class post_widget(QtWidgets.QFrame):

    post_signal = pyqtSignal(int)

    def __init__(self, parent = None):
        super(post_widget, self).__init__(parent)
        self.build_ui()
        self.connect_functions()

    def build_ui(self):
        self.setObjectName('ticket_message_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)
        
        self.content_textEdit = QtWidgets.QTextEdit()
        self.content_textEdit.setMaximumHeight(100)
        self.content_textEdit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.content_textEdit.setPlaceholderText('Your message here')
        self.main_layout.addWidget(self.content_textEdit)

        self.drop_files_widget = drop_files_widget.drop_files_widget()
        self.main_layout.addWidget(self.drop_files_widget)

        self.footer_widget = QtWidgets.QWidget()
        self.footer_widget.setObjectName('transparent_widget')
        self.footer_layout = QtWidgets.QHBoxLayout()
        self.footer_layout.setContentsMargins(0,0,0,0)
        self.footer_layout.setSpacing(6)
        self.footer_widget.setLayout(self.footer_layout)
        self.main_layout.addWidget(self.footer_widget)

        self.footer_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.post_and_close_button = QtWidgets.QPushButton('Post and close ticket')
        self.post_and_close_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.footer_layout.addWidget(self.post_and_close_button)

        self.post_button = QtWidgets.QPushButton('Post')
        self.post_button.setObjectName('blue_button')
        self.post_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.footer_layout.addWidget(self.post_button)

    def clear(self):
        self.content_textEdit.clear()
        self.drop_files_widget.clear()

    def connect_functions(self):
        self.post_button.clicked.connect(self.post_signal.emit)

    def post(self, ticket_id):
        if ticket_id is not None:
            message = self.content_textEdit.toPlainText()
            files = self.drop_files_widget.files()
            if assets.add_ticket_message(ticket_id, message, files):
                gui_server.refresh_ui()
            self.clear()