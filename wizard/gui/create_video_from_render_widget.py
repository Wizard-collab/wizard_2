# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import ocio_utils
from wizard.core import video
from wizard.core import project
from wizard.core import subtasks_library
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class create_video_from_render_widget(QtWidgets.QDialog):
    def __init__(self, export_version_id, parent=None):
        super(create_video_from_render_widget, self).__init__()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Wizard - Create video from render")

        self.export_version_id = export_version_id
        self.build_ui()
        self.connect_functions()

    def connect_functions(self):
        self.reject_button.clicked.connect(self.reject)
        self.create_button.clicked.connect(self.create_video)

    def showEvent(self, event):
        event.accept()
        QtWidgets.QApplication.processEvents()
        self.fill_ui()

    def fill_ui(self):
        available_color_spaces = ocio_utils.get_OCIO_available_color_spaces()
        for color_space in available_color_spaces:
            self.input_color_space_combobox.addItem(color_space)
            self.output_color_space_combobox.addItem(color_space)
        if 'ACES - ACEScg' in available_color_spaces:
            self.input_color_space_combobox.setCurrentText('ACES - ACEScg')
        if 'out_srgb' in available_color_spaces:
            self.output_color_space_combobox.setCurrentText('out_srgb')
        frame_rate = project.get_frame_rate()
        self.frame_rate_spinBox.setValue(frame_rate)

    def create_video(self):
        subtasks_library.create_video_from_render(self.export_version_id,
                                self.input_color_space_combobox.currentText(),
                                self.output_color_space_combobox.currentText(),
                                self.frame_rate_spinBox.value(),
                                comment=self.comment_textEdit.toPlainText(),
                                overlay = self.burn_details_checkbox.isChecked())
        self.accept()

    def build_ui(self):
        self.resize(500,250)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(8)
        self.setLayout(self.main_layout)

        self.form_layout = QtWidgets.QFormLayout()
        self.main_layout.addLayout(self.form_layout)

        self.input_color_space_combobox = gui_utils.QComboBox()
        self.form_layout.addRow(QtWidgets.QLabel('Input color space'), self.input_color_space_combobox)

        self.output_color_space_combobox = gui_utils.QComboBox()
        self.form_layout.addRow(QtWidgets.QLabel('Output color space'), self.output_color_space_combobox)

        self.frame_rate_spinBox = QtWidgets.QSpinBox()
        self.frame_rate_spinBox.setButtonSymbols(QtWidgets.QSpinBox.ButtonSymbols.NoButtons)
        self.form_layout.addRow(self.frame_rate_spinBox)

        self.burn_details_checkbox = QtWidgets.QCheckBox("Burn details")
        self.burn_details_checkbox.setChecked(True)
        self.form_layout.addRow(self.burn_details_checkbox)

        self.comment_textEdit = QtWidgets.QTextEdit()
        self.comment_textEdit.setPlaceholderText('Your comment here')
        self.comment_textEdit.setMaximumHeight(100)
        self.main_layout.addWidget(self.comment_textEdit)

        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setContentsMargins(0,0,0,0)
        self.buttons_layout.setSpacing(4)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        self.buttons_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.reject_button = QtWidgets.QPushButton('Cancel')
        self.reject_button.setDefault(False)
        self.reject_button.setAutoDefault(False)
        self.buttons_layout.addWidget(self.reject_button)

        self.create_button = QtWidgets.QPushButton('Create video')
        self.create_button.setObjectName('blue_button')
        self.create_button.setDefault(True)
        self.create_button.setAutoDefault(True)
        self.buttons_layout.addWidget(self.create_button)
