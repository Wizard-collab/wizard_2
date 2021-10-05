# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com
    
# Python modules
from PySide2 import QtWidgets, QtGui
import os
import json

# Substance Painter modules
import substance_painter.logging as logging

# Wizard modules
import wizard_communicate

image_sizes = ['128',
                '256',
                '512',
                '1024',
                '2048',
                '4096',
                '8192']
file_types = ['bmp',
                'ico',
                'jpeg',
                'jng',
                'pbm',
                'pgm',
                'png',
                'ppm',
                'targa',
                'tiff',
                'wbmp',
                'xpm',
                'gif',
                'hdr',
                'exr',
                'j2k',
                'jp2',
                'pfm',
                'webp',
                'jpeg-xr',
                'psd']

class export_ui(QtWidgets.QDialog):
    def __init__(self):
        super(export_ui, self).__init__()
        self.setWindowTitle('Wizard export')
        self.build_ui()
        self.get_settings_file()
        self.load_settings()
        self.connect_functions()

    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.material_lineEdit = QtWidgets.QLineEdit()
        self.material_lineEdit.setPlaceholderText('Material')
        self.main_layout.addWidget(self.material_lineEdit)

        self.image_sizes_comboBox = QtWidgets.QComboBox()
        self.image_sizes_comboBox.addItems(image_sizes)
        self.main_layout.addWidget(self.image_sizes_comboBox)

        self.file_formats_comboBox = QtWidgets.QComboBox()
        self.file_formats_comboBox.addItems(file_types)
        self.main_layout.addWidget(self.file_formats_comboBox)

        self.save_params_button = QtWidgets.QPushButton('Save preferences')
        save_preferences_icon = os.path.abspath("icons/save_increment.png")
        self.save_params_button.setIcon(QtGui.QIcon(save_preferences_icon))
        self.main_layout.addWidget(self.save_params_button)

        self.export_button = QtWidgets.QPushButton('Export')
        export_icon = os.path.abspath("icons/export.png")
        self.export_button.setIcon(QtGui.QIcon(export_icon))
        self.main_layout.addWidget(self.export_button)
        self.export_button.setDefault(True)

    def get_settings_file(self):
        user_folder = os.path.join(wizard_communicate.get_user_folder(),
                                    'substance_painter')
        self.settings_file = os.path.join(user_folder, 'preferences.json')
        if not os.path.isdir(user_folder):
            os.makedirs(user_folder)

    def load_settings(self):
        if not os.path.isfile(self.settings_file):
            self.save_preferences('PBR Metallic Roughness', '4096', 'exr')
        with open(self.settings_file, 'r') as f:
            preferences_dic = json.load(f)
        self.material_lineEdit.setText(preferences_dic['material'])
        self.image_sizes_comboBox.setCurrentText(preferences_dic['size'])
        self.file_formats_comboBox.setCurrentText(preferences_dic['type'])

    def export(self):
        self.material = self.material_lineEdit.text()
        self.size = self.image_sizes_comboBox.currentText()
        self.type = self.file_formats_comboBox.currentText()
        self.save_preferences(material=None, size=None, type=None)
        self.accept()

    def save_preferences(self, material=None, size=None, type=None):
        if not material:
            material = self.material_lineEdit.text()
        if not size:
            size = self.image_sizes_comboBox.currentText()
        if not type:
            type = self.file_formats_comboBox.currentText()
        preferences_dic = dict()
        preferences_dic['material'] = material
        preferences_dic['size'] = size
        preferences_dic['type'] = type
        with open(self.settings_file, 'w') as f:
            json.dump(preferences_dic, f)
        logging.info('Export preferences saved')

    def connect_functions(self):
        self.export_button.clicked.connect(self.export)
        self.save_params_button.clicked.connect(self.save_preferences)
