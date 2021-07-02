# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import project
from wizard.core import assets
from wizard.core import site

# Wizard gui modules
from wizard.gui import drop_files_widget

class create_ticket_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(create_ticket_widget, self).__init__(parent)
        self.build_ui()
        self.fill_ui()
        self.connect_functions()

    def submit(self):
        title = self.title_lineEdit.text()
        destination_user = self.destination_comboBox.currentText()
        if destination_user == 'everybody':
            destination_user = None
        content = self.content_textEdit.toPlainText()
        files = self.drop_files_widget.files()
        if assets.create_ticket(title, content, 1, destination_user, files):
            self.close()

    def connect_functions(self):
        self.submit_button.clicked.connect(self.submit)
        self.quit_button.clicked.connect(self.close)

    def fill_ui(self):
        self.destination_comboBox.addItem('everybody')
        for user_id in project.get_users_ids_list():
            user_name = site.get_user_data(user_id, 'user_name')
            self.destination_comboBox.addItem(user_name)

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.title_label = QtWidgets.QLabel('New ticket')
        self.title_label.setObjectName('title_label')
        self.main_layout.addWidget(self.title_label)

        self.infos_label = QtWidgets.QLabel('This ticket is about characters | Joe | modeling | main | main | 0002')
        self.infos_label.setWordWrap(True)
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.title_lineEdit = QtWidgets.QLineEdit()
        self.title_lineEdit.setPlaceholderText('Ticket title')
        self.header_layout.addWidget(self.title_lineEdit)

        self.destination_comboBox = QtWidgets.QComboBox()
        self.destination_comboBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.header_layout.addWidget(self.destination_comboBox)

        self.content_textEdit = QtWidgets.QTextEdit()
        self.content_textEdit.setPlaceholderText('Your message here')
        self.main_layout.addWidget(self.content_textEdit)

        self.drop_files_widget = drop_files_widget.drop_files_widget()
        self.main_layout.addWidget(self.drop_files_widget)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.spaceItem = QtWidgets.QSpacerItem(100,0,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.Fixed)
        self.buttons_layout.addSpacerItem(self.spaceItem)

        self.quit_button = QtWidgets.QPushButton('Cancel')
        self.buttons_layout.addWidget(self.quit_button)
        self.submit_button = QtWidgets.QPushButton('Submit')
        self.submit_button.setObjectName('blue_button')
        self.buttons_layout.addWidget(self.submit_button)