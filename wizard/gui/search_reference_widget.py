# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
import logging
import time
import traceback

# Wizard modules
from wizard.core import user
from wizard.core import project
from wizard.vars import ressources
from wizard.vars import assets_vars

# Wizard gui modules
from wizard.gui import gui_utils

logger = logging.getLogger(__name__)


class search_reference_widget(QtWidgets.QWidget):

    stage_ids_signal = pyqtSignal(list)
    groups_ids_signal = pyqtSignal(list)

    def __init__(self, context, parent=None):
        super(search_reference_widget, self).__init__(parent)

        self.init_icons_dic()

        self.parent = parent
        self.context = context
        self.old_thread_id = None
        self.search_threads = dict()

        self.setWindowIcon(QtGui.QIcon(ressources._wizard_ico_))
        self.setWindowTitle(f"Create references")

        self.accept_item_from_thread = True

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.stage_ids = dict()
        self.groups_ids = dict()

        self.build_ui()
        self.load_context()

        self.click_detector = gui_utils.GlobalClickDetector(self)
        QtWidgets.QApplication.instance().installEventFilter(self.click_detector)

        self.connect_functions()

    def load_context(self):
        reference_auto_update_default = user.user().get_reference_auto_update_default()
        self.reference_with_auto_update_checkBox.setChecked(
            reference_auto_update_default)

    def set_context(self):
        reference_auto_update_default = self.reference_with_auto_update_checkBox.isChecked()
        user.user().set_reference_auto_update_default(reference_auto_update_default)

    def init_icons_dic(self):
        self.icons_dic = dict()
        for stage in assets_vars._all_stages_:
            self.icons_dic[stage] = QtGui.QIcon(
                ressources._stage_icons_dic_[stage])

    def move_ui(self):
        cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        area = self.parent.rect()
        if area.contains(cursor):
            screen_minX = area.topLeft().x()
            screen_minY = area.topLeft().y()
            screen_maxX = area.bottomRight().x()
            screen_maxY = area.bottomRight().y()
            win_width = self.frameSize().width()
            win_heigth = self.frameSize().height()

            if (cursor.y() - 120 - win_heigth) <= screen_minY:
                posy = cursor.y() - 12
                angley = 'top'
            else:
                posy = cursor.y() - win_heigth + 12
                angley = 'bottom'
            if (cursor.x() + 120 + win_width) >= screen_maxX:
                posx = cursor.x() - win_width + 12
                anglex = 'right'
            else:
                posx = cursor.x() - 12
                anglex = 'left'

            self.move(posx, posy)
        else:
            self.close()

    def showEvent(self, event):
        self.move_ui()
        self.search_bar.search_bar.setFocus()
        event.accept()

    def clear(self):
        self.search_bar.setText('')

    def focus_out(self):
        QtWidgets.QApplication.instance().removeEventFilter(self.click_detector)
        self.close()

    def search_ended(self):
        search_time = str(
            round((time.perf_counter()-self.search_start_time), 3))
        self.found_label.setText(
            f"Found {self.list_view.invisibleRootItem().childCount()} occurences in {search_time}s")
        if self.list_view.invisibleRootItem().childCount() == 0:
            self.show_info_mode('No export found...',
                                ressources._nothing_info_)
        else:
            self.hide_info_mode()

    def clean_threads(self):
        ids = list(self.search_threads.keys())
        for thread_id in ids:
            if not self.search_threads[thread_id].running:
                self.search_threads[thread_id].terminate()
                del self.search_threads[thread_id]

    def search_asset(self, search):
        self.search_start_time = time.perf_counter()
        self.accept_item_from_thread = False
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
            self.search_threads[self.old_thread_id].item_signal.disconnect()
            self.search_threads[self.old_thread_id].group_signal.disconnect()
            self.search_threads[self.old_thread_id].search_ended.disconnect()
        thread_id = time.time()
        self.search_threads[thread_id] = search_thread(self.context)
        self.search_threads[thread_id].item_signal.connect(self.add_item)
        self.search_threads[thread_id].group_signal.connect(self.add_group)
        self.search_threads[thread_id].search_ended.connect(self.search_ended)
        self.old_thread_id = thread_id
        self.list_view.clear()
        self.stage_ids = dict()
        self.groups_ids = dict()
        if len(search) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(search)
        else:
            self.search_threads[thread_id].running = False
            self.search_ended()
        self.clean_threads()

    def add_item(self, item_list):
        if self.accept_item_from_thread:
            if item_list[2]['id'] not in self.stage_ids.keys():
                stage_item = custom_item(
                    item_list[0], item_list[1], item_list[2], self.icons_dic, self.list_view.invisibleRootItem())
                self.stage_ids[item_list[2]['id']] = stage_item

    def add_group(self, group_row):
        if self.accept_item_from_thread:
            if group_row['id'] not in self.groups_ids.keys():
                group_item = custom_group_item(
                    group_row, self.list_view.invisibleRootItem())
                self.groups_ids[group_row['id']] = group_item

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.search_asset)
        self.list_view.itemDoubleClicked.connect(self.return_references)
        self.reference_with_auto_update_checkBox.stateChanged.connect(
            self.set_context)
        self.click_detector.clicked_outside.connect(self.focus_out)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Down:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Up:
            self.list_view.keyPressEvent(event)
        if event.key() == QtCore.Qt.Key.Key_Return:
            self.return_references()
        event.accept()

    def return_references(self):
        selected_items = self.list_view.selectedItems()
        if selected_items is not None and len(selected_items) >= 1:
            stage_ids = []
            groups_ids = []
            for selected_item in selected_items:
                if selected_item.type == 'stage':
                    stage_ids.append(selected_item.stage_row['id'])
                elif selected_item.type == 'group':
                    groups_ids.append(selected_item.group_row['id'])
            if stage_ids != []:
                self.stage_ids_signal.emit(stage_ids)
            if groups_ids != []:
                self.groups_ids_signal.emit(groups_ids)
            self.close()

    def show_info_mode(self, text, image):
        self.list_view.setVisible(0)
        self.info_widget.setVisible(1)
        self.info_widget.setText(text)
        self.info_widget.setImage(image)

    def hide_info_mode(self):
        self.info_widget.setVisible(0)
        self.list_view.setVisible(1)

    def build_ui(self):
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                           QtWidgets.QSizePolicy.Policy.Preferred)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setObjectName('dark_widget')
        self.main_widget.setStyleSheet('border-radius:5px;')
        self.main_widget_layout = QtWidgets.QVBoxLayout()
        self.main_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.main_widget_layout.setSpacing(0)
        self.main_widget.setLayout(self.main_widget_layout)
        self.main_layout.addWidget(self.main_widget)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(70)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.shadow.setXOffset(2)
        self.shadow.setYOffset(2)
        self.main_widget.setGraphicsEffect(self.shadow)

        self.search_bar = gui_utils.search_bar()
        self.search_bar.setPlaceholderText(
            '"Joe", "characters&Joe", "INTRO&animation"')
        self.main_widget_layout.addWidget(self.search_bar)

        self.found_widget = QtWidgets.QWidget()
        self.found_widget.setObjectName('dark_widget')
        self.found_layout = QtWidgets.QHBoxLayout()
        self.found_widget.setLayout(self.found_layout)
        self.main_widget_layout.addWidget(self.found_widget)
        self.found_label = QtWidgets.QLabel()
        self.found_label.setObjectName('gray_label')
        self.found_layout.addWidget(self.found_label)

        self.info_widget = gui_utils.info_widget()
        self.info_widget.setVisible(0)
        self.main_widget_layout.addWidget(self.info_widget)

        self.list_view = QtWidgets.QTreeWidget()
        self.list_view.setObjectName('tree_as_list_widget')
        self.list_view.setStyleSheet(
            'border-top-left-radius:0px;border-top-right-radius:0px;')
        self.list_view.setColumnCount(4)
        self.list_view.setHeaderHidden(True)
        self.list_view.setIndentation(0)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.header().resizeSection(0, 100)
        self.list_view.header().resizeSection(1, 150)
        self.list_view.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.main_widget_layout.addWidget(self.list_view)
        self.show_info_mode('No export found...', ressources._nothing_info_)

        self.settings_widget = QtWidgets.QWidget()
        self.settings_layout = QtWidgets.QHBoxLayout()
        self.settings_widget.setLayout(self.settings_layout)
        self.main_widget_layout.addWidget(self.settings_widget)

        self.settings_layout.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))

        self.reference_with_auto_update_checkBox = QtWidgets.QCheckBox(
            "Reference with auto update")
        self.settings_layout.addWidget(
            self.reference_with_auto_update_checkBox)


class search_thread(QtCore.QThread):

    item_signal = pyqtSignal(list)
    group_signal = pyqtSignal(object)
    search_ended = pyqtSignal(int)

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.running = True

    def update_search(self, string):
        self.string = string
        self.start()

    def run(self):
        try:
            keywords = self.string.split('&')
            all_export_versions_stage_ids = project.get_all_export_versions(
                'stage_id')
            # all_variants = project.get_all_variants()
            all_stages = project.get_all_stages()
            all_assets = project.get_all_assets()
            all_categories = project.get_all_categories()
            stages = dict()
            for stage_row in all_stages:
                stages[stage_row['id']] = stage_row
            assets = dict()
            for asset_row in all_assets:
                assets[asset_row['id']] = asset_row
            categories = dict()
            for category_row in all_categories:
                categories[category_row['id']] = category_row
            for stage_row in all_stages:
                if stage_row['id'] in all_export_versions_stage_ids:
                    if all(keyword.upper() in stage_row['string'].upper() for keyword in keywords):
                        asset_row = assets[stage_row['asset_id']]
                        category_row = categories[asset_row['category_id']]
                        self.item_signal.emit(
                            [category_row, asset_row, stage_row])
            if (self.context == 'work_env'):
                groups_rows = project.get_groups()
                for group_row in groups_rows:
                    if all(keyword.upper() in group_row['name'].upper()+'GROUPS' for keyword in keywords):
                        self.group_signal.emit(group_row)
            self.search_ended.emit(1)
            self.running = False
        except:
            logger.critical(str(traceback.format_exc()))


class custom_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, category_row, asset_row, stage_row, icons_dic, parent=None):
        super(custom_item, self).__init__(parent)
        self.type = 'stage'
        self.icons_dic = icons_dic
        self.category_row = category_row
        self.asset_row = asset_row
        self.stage_row = stage_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(0, self.category_row['name'])
        self.setText(1, self.asset_row['name'])
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
        self.setText(2, self.stage_row['name'])
        self.setIcon(2, self.icons_dic[self.stage_row['name']])


class custom_group_item(QtWidgets.QTreeWidgetItem):
    def __init__(self, group_row, parent=None):
        super(custom_group_item, self).__init__(parent)
        self.type = 'group'
        self.group_row = group_row
        self.fill_ui()

    def fill_ui(self):
        self.setText(1, self.group_row['name'])
        self.setText(0, 'group')
        self.setIcon(1, gui_utils.QIcon_from_svg(ressources._group_icon_,
                                                 self.group_row['color']))
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        self.setFont(1, bold_font)
