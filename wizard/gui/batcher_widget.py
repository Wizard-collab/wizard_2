# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
import logging
import os
import importlib
import traceback
import sys

# Wizard gui modules
from wizard.gui import gui_utils

# Wizard modules
from wizard.core import path_utils
from wizard.vars import ressources

logger = logging.getLogger(__name__)

class batcher_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(batcher_widget, self).__init__(parent)
        self.current_script_widget = None
        self.scripts_dic = dict()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Batcher")

        self.build_ui()
        self.connect_functions()

    def toggle(self):
        if self.isVisible():
            if not self.isActiveWindow():
                self.show()
                self.raise_()
                self.refresh()
            else:
                self.hide()
        else:
            self.show()
            self.raise_()
            self.refresh()

    def build_ui(self):
        self.resize(1000, 600)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.scripts_comboBox = gui_utils.QComboBox()
        self.main_layout.addWidget(self.scripts_comboBox)

        self.description_label = QtWidgets.QLabel()
        self.description_label.setObjectName('gray_label')
        self.main_layout.addWidget(self.description_label)

        self.scripts_widgets_frame = QtWidgets.QFrame()
        self.scripts_widgets_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.scripts_widgets_frame.setObjectName("dark_round_frame")
        self.scripts_widgets_frame.setStyleSheet("#dark_round_frame{border:1px solid rgba(255,255,255,10);}")
        self.scripts_widgets_layout = QtWidgets.QHBoxLayout()
        self.scripts_widgets_frame.setLayout(self.scripts_widgets_layout)
        self.main_layout.addWidget(self.scripts_widgets_frame)

    def connect_functions(self):
        self.scripts_comboBox.currentTextChanged.connect(self.current_script_item_changed)

    def refresh(self):
        scripts = []
        for file in path_utils.listdir("ressources/batcher_scripts"):
            if not file.endswith('.py'):
                continue
            script_path = path_utils.join("ressources/batcher_scripts", file)
            if script_path in scripts:
                continue
            scripts.append(script_path)

        for script in scripts:
            module = load_module(script)
            batch_script_name = module.name
            if batch_script_name in self.scripts_dic.keys():
                continue
            self.scripts_dic[batch_script_name] = module
            self.scripts_comboBox.addItem(QtGui.QIcon(module.icon), batch_script_name)

    def current_script_item_changed(self):
        if self.current_script_widget is not None:
            self.current_script_widget.setVisible(False)
            self.current_script_widget.setParent(None)
            self.current_script_widget.deleteLater()
        selected_script = self.scripts_comboBox.currentText()
        module = self.scripts_dic[selected_script]
        self.description_label.setText(module.description)
        self.current_script_widget = module.widget()
        self.scripts_widgets_layout.addWidget(self.current_script_widget)

def load_module(module_path):
    try:
        if not os.path.isfile(module_path):
            logger.info("Module {0} not found, skipping".format(module_path))
            return None
        else:
            module_name = path_utils.basename(module_path).split('.')[0]
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module 
            spec.loader.exec_module(module)
            return module
    except:
        logger.info("Can't load module {0}, skipping".format(module_path))
        logger.error(traceback.format_exc())
        return None