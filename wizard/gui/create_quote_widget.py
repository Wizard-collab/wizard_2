# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

# Wizard modules
from wizard.core import site
from wizard.vars import ressources

class create_quote_widget(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(create_quote_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create quote")

        self.build_ui()
        self.connect_functions()

    def update_count(self):
        content = self.quote_field.toPlainText()
        self.count_label.setText(f'{str(len(content))}/100 characters')
        if len(content)>100:
            self.count_label.setStyleSheet('color:#f0605b;')
        else:
            self.count_label.setStyleSheet('')

    def connect_functions(self):
        self.quote_field.textChanged.connect(self.update_count)
        self.accept_button.clicked.connect(self.create_quote)
        self.cancel_button.clicked.connect(self.reject)

    def create_quote(self):
        content = self.quote_field.toPlainText()
        if site.add_quote(content):
            self.accept()

    def build_ui(self):
        self.setMinimumWidth(350)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)

        self.infos_label = QtWidgets.QLabel('Warning, the quotes are not anonymous')
        self.infos_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.infos_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.MinimumExpanding))

        self.count_label = QtWidgets.QLabel('0/100 characters')
        self.main_layout.addWidget(self.count_label)

        self.quote_field = QtWidgets.QTextEdit()
        self.quote_field.setMaximumHeight(200)
        self.quote_field.setPlaceholderText("Your quote here...")
        self.main_layout.addWidget(self.quote_field)

        self.warning_frame = QtWidgets.QFrame()
        self.warning_layout = QtWidgets.QHBoxLayout()
        self.warning_layout.setAlignment(QtCore.Qt.AlignTop)
        self.warning_layout.setContentsMargins(6,6,6,6)
        self.warning_layout.setSpacing(6)
        self.warning_frame.setLayout(self.warning_layout)
        self.main_layout.addWidget(self.warning_frame)

        self.warning_icon = QtWidgets.QLabel()
        self.warning_icon.setAlignment(QtCore.Qt.AlignTop)
        self.warning_icon.setPixmap(QtGui.QIcon(ressources._agreement_icon_).pixmap(30))
        self.warning_icon.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.warning_layout.addWidget(self.warning_icon)

        warning_text = "Please ensure that you're respectful, everybody has access to your publication.\n"
        warning_text += "Do not name anybody.\n"
        warning_text += "Every publication is submitted to the technical team.\n"
        warning_text += "If the publication doesn't match the chart, you will be asked to delete it.\n"
        self.warning_label = QtWidgets.QLabel(warning_text)
        self.warning_layout.addWidget(self.warning_label)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding,
                                                    QtWidgets.QSizePolicy.MinimumExpanding))

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(6)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.cancel_button = QtWidgets.QPushButton('Cancel')
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.cancel_button)

        self.accept_button = QtWidgets.QPushButton('Add')
        self.accept_button.setObjectName('blue_button')
        self.accept_button.setDefault(True)
        self.accept_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.accept_button)
