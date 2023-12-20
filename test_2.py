import test
from wizard.gui import app_utils
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import datetime
import time
import random
from wizard.core import project
from wizard.core import assets
from wizard.vars import ressources
from wizard.gui import gui_utils
from wizard.core import image
from wizard.core import repository
import copy

class signal_manager(QtCore.QObject):

    item_updated = pyqtSignal(object)

    def __init__(self, parent=None):
        super(signal_manager, self).__init__(parent)

class calendar_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendar_widget, self).__init__(parent)

        self.resize(800, 600)

        self.header_view = test.calendar_header()
        self.view = test.calendar_viewport()
        self.grouped_dic = dict()
        self.group_method = 'stage'
        self.group_methods_list = ['stage', 'domain', 'category', 'asset', 'state', 'assignment', 'priority']
        self.stage_ids = dict()
        self.grouped_dic['frames'] = dict()

        self.old_thread_id = None
        self.search_threads = dict()

        self.init_users_images()
        self.init_priority_images_dic()
        self.build_ui()
        self.connect_functions()

        self.view.set_zoom(0.5)
        #self.refresh()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 28, 12)
            self.users_images_dic[user_row['user_name']] = pixmap

    def init_priority_images_dic(self):
        self.priority_images_dic = dict()
        for priority in ressources._priority_icons_list_.keys():
            priority_image =  ressources._priority_icons_list_[priority]
            pixmap = QtGui.QIcon(priority_image).pixmap(28)
            self.priority_images_dic[priority] = pixmap

    def showEvent(self, event):
        self.group_methods_comboBox.clear()
        for group_method in self.group_methods_list:
            self.group_methods_comboBox.addItem(group_method)

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)
        self.group_methods_comboBox.currentTextChanged.connect(self.change_group_method)
        self.search_bar.textChanged.connect(self.update_search)

    def change_group_method(self):
        self.group_method = self.group_methods_comboBox.currentText()
        self.refresh()

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(1)
        self.setLayout(self.main_layout)

        self.header_widget = QtWidgets.QWidget()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)
        self.main_layout.addWidget(self.header_widget)

        self.group_label =  QtWidgets.QLabel('Group by')
        self.header_layout.addWidget(self.group_label)
        self.group_methods_comboBox = gui_utils.QComboBox()
        self.header_layout.addWidget(self.group_methods_comboBox)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.search_bar = gui_utils.search_bar(red=36, green=36, blue=43)
        self.header_layout.addWidget(self.search_bar)

        self.header_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))

        self.main_layout.addWidget(self.header_view)
        self.main_layout.addWidget(self.view)

    def update_search(self):
        if not self.isVisible():
            return
        search_data = self.search_bar.text()
        self.search_start_time = time.perf_counter()
        self.accept_item_from_thread = False
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
            self.search_threads[self.old_thread_id].show_stage_signal.disconnect()
            self.search_threads[self.old_thread_id].hide_stage_signal.disconnect()
        thread_id = time.time()
        self.search_threads[thread_id] = search_thread()
        self.search_threads[thread_id].show_stage_signal.connect(self.show_stage)
        self.search_threads[thread_id].hide_stage_signal.connect(self.hide_stage)
        self.old_thread_id = thread_id
        if len(search_data) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(self.stage_rows, search_data)
        else:
            self.search_threads[thread_id].running=False
            self.show_all_stages()
        self.clean_threads()

    def show_stage(self, stage_id):
        if stage_id not in self.stage_ids.keys():
            return
        self.stage_ids[stage_id].setVisible(True)
        self.update_frames_visibility()
        self.organize_items()        

    def hide_stage(self, stage_id):
        if stage_id not in self.stage_ids.keys():
            return
        self.stage_ids[stage_id].setVisible(False)
        self.update_frames_visibility()
        self.organize_items()        

    def show_all_stages(self):
        for stage_id in self.stage_ids.keys():
            self.show_stage(stage_id)
        self.update_frames_visibility()
        self.organize_items()        

    def update_frames_visibility(self):
        for group_name in self.grouped_dic['frames'].keys():
            visibility = False
            for item in self.grouped_dic['frames'][group_name]['items']:
                if not item.isVisible():
                    continue
                visibility = True
            self.grouped_dic['frames'][group_name]['frame_item'].setVisible(visibility)

    def clean_threads(self):
        ids = list(self.search_threads.keys())
        for thread_id in ids:
            if not self.search_threads[thread_id].running:
                self.search_threads[thread_id].terminate()
                del self.search_threads[thread_id]

    def get_group_name(self, domain_row, category_row, asset_row, stage_row):
        if self.group_method == 'stage':
            group_name = stage_row['name']
        elif self.group_method == 'domain':
            group_name = domain_row['name']
        elif self.group_method == 'category':
            group_name = category_row['name']
        elif self.group_method == 'asset':
            group_name = f"{category_row['name']}/{asset_row['name']}"
        elif self.group_method == 'state':
            group_name = stage_row['state']
        elif self.group_method == 'assignment':
            group_name = stage_row['assignment']
        elif self.group_method == 'priority':
            group_name = stage_row['priority']
        return group_name

    def refresh(self):

        project_stages = []
        self.stage_rows = []

        domains = project.get_domains()
        for domain_row in domains:
            if domain_row['name'] == 'library':
                continue
            for category_row in project.get_domain_childs(domain_row['id']):
                assets = project.get_category_childs(category_row['id'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    for stage_row in stages:
                        self.stage_rows.append(stage_row)
                        project_stages.append(stage_row['id'])

                        group_name = self.get_group_name(domain_row, category_row, asset_row, stage_row)
                        if group_name not in self.grouped_dic['frames'].keys():
                            self.grouped_dic['frames'][group_name] = dict()
                            frame = frame_item(group_name, '#1d1d23')
                            self.grouped_dic['frames'][group_name]['frame_item'] = frame
                            self.grouped_dic['frames'][group_name]['items'] = []
                            self.view.add_frame(frame)

                        if stage_row['id'] not in self.stage_ids.keys():

                            item = stage_item(stage_row, datetime.datetime.fromtimestamp(stage_row['start_date']),
                                                int(stage_row['estimated_time']),
                                                bg_color = ressources._stages_colors_[stage_row['name']],
                                                users_images_dic = self.users_images_dic,
                                                priority_images_dic = self.priority_images_dic)
                            self.view.add_item(item)
                            item.stage_item_signal_manager.item_updated.connect(self.update_frames)
                            self.stage_ids[stage_row['id']] = item

                        else:
                            self.stage_ids[stage_row['id']].stage_row = stage_row

                        for other_group in self.grouped_dic['frames'].keys():
                            if other_group != group_name:
                                if self.stage_ids[stage_row['id']] in self.grouped_dic['frames'][other_group]['items']:
                                    self.grouped_dic['frames'][other_group]['items'].remove(self.stage_ids[stage_row['id']])
                            else:
                                if self.stage_ids[stage_row['id']] not in self.grouped_dic['frames'][other_group]['items']:
                                    self.grouped_dic['frames'][other_group]['items'].append(self.stage_ids[stage_row['id']])

        stage_ids = list(self.stage_ids.keys())
        for stage_id in stage_ids:
            if stage_id not in project_stages:
                self.remove_stage(stage_id)

        groups_list = list(self.grouped_dic['frames'].keys())
        for group_name in groups_list:
            if len(self.grouped_dic['frames'][group_name]['items']) == 0:
                self.remove_frame(group_name)

        ordered_items = []
        for group_name in self.grouped_dic['frames'].keys():
            ordered_items.append(self.grouped_dic['frames'][group_name]['items'])

        self.organize_items()        

    def organize_items(self):
        self.view.reset_y_pos()
        for group_name in self.grouped_dic['frames'].keys():
            if self.grouped_dic['frames'][group_name]['frame_item'].isVisible():
                self.view.add_space(120)
            self.view.organize_items(self.grouped_dic['frames'][group_name]['items'])
        self.update_frames()

    def remove_stage(self, stage_id):
        if stage_id not in self.stage_ids.keys():
            return
        item = self.stage_ids[stage_id]
        self.view.remove_item(item)
        for group_name in self.grouped_dic['frames'].keys():
            if item in self.grouped_dic['frames'][group_name]['items']:
                self.grouped_dic['frames'][group_name]['items'].remove(item)
        del self.stage_ids[stage_id]
        del item

    def remove_frame(self, group_name):
        if group_name in self.grouped_dic['frames'].keys():
            self.view.remove_frame(self.grouped_dic['frames'][group_name]['frame_item'])
            del self.grouped_dic['frames'][group_name]['frame_item']
            del self.grouped_dic['frames'][group_name]

    def update_frame_bouding_rect(self, group_name):
        visible_items = []
        for item in self.grouped_dic['frames'][group_name]['items']:
            if not item.isVisible():
                continue
            visible_items.append(item)
        if len(visible_items) == 0:
            return
        bounding_rect = visible_items[0].sceneBoundingRect()
        for item in visible_items[1:]:
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        self.grouped_dic['frames'][group_name]['frame_item'].update_rect(bounding_rect)

    def update_frames(self):
        for group_name in self.grouped_dic['frames'].keys():
            self.update_frame_bouding_rect(group_name)

class stage_item(test.calendar_item):
    def __init__(self, stage_row, date, duration, bg_color, users_images_dic, priority_images_dic):
        super(stage_item, self).__init__(date=date, duration=duration, bg_color=bg_color)
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic
        self.priority_images_dic = priority_images_dic
        self.stage_item_signal_manager = signal_manager()
        self.connect_functions()

    def connect_functions(self):
        self.signal_manager.start_date_modified.connect(self.apply_start_date)
        self.signal_manager.duration_modified.connect(self.apply_duration)

    def apply_start_date(self):
        start_date = int(self.date.timestamp())
        assets.modify_stage_start_date(self.stage_row['id'], start_date)

    def apply_duration(self):
        assets.modify_stage_estimation(self.stage_row['id'], int(self.duration))

    def paint(self, painter, option, widget):
        super(stage_item, self).paint(painter, option, widget)
        if self.scene().zoom_factor > 0.15:
            rect = self.client_rect().toRect()
            margin = 2
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            painter.drawPixmap(rect.x()+margin, rect.y()+margin, self.users_images_dic[self.stage_row['assignment']])
            state_rect = QtCore.QRect(rect.x() + 28 + margin*2, rect.y() + margin, 50, rect.height()-margin*2)
            test.draw_rect(painter, state_rect, bg_color=QtGui.QColor(ressources._states_colors_[self.stage_row['state']]), radius=2)
            test.draw_text(painter, state_rect, self.stage_row['state'], size=18, align=QtCore.Qt.AlignCenter, bold=True)
            painter.drawPixmap(rect.x() + margin*4 + 50 + 28, rect.y(), self.priority_images_dic[self.stage_row['priority']])

        if self.scene().zoom_factor > 0.23:
            text_rect = QtCore.QRect(rect.x() + margin*6 + 50 + 28+28, rect.y(), 500, rect.height())
            zoom_factor = self.scene().zoom_factor
            stage_text = self.stage_row['string'].split('/')
            stage_text.pop(0)
            stage_text = f"{('/').join(stage_text)} - {int(self.duration)} day"
            test.draw_text(painter, text_rect, stage_text, size=20, align=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.stage_item_signal_manager.item_updated.emit(self)

class frame_item(test.frame_item):
    def __init__(self, group_name, bg_color):
        super(frame_item, self).__init__(bg_color=bg_color, frame_label=group_name)
        self.margin = 20
        self.group_name = group_name
        self.setZValue(-1)

    def update_rect(self, rect):
        self.setPos(rect.x()-self.margin, rect.y()-self.margin)
        self.prepareGeometryChange()
        self.width = rect.width()+self.margin*2
        self.height = rect.height()+self.margin*2

class search_thread(QtCore.QThread):

    show_stage_signal = pyqtSignal(int)
    hide_stage_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def update_search(self, stage_rows, search_data):
        self.search_data = search_data
        self.stage_rows = copy.deepcopy(stage_rows)
        self.start()

    def run(self):
        try:
            stages_to_show = []
            stages_to_hide = []

            keywords_sets = self.search_data.split('+')
            
            for stage_row in self.stage_rows:

                stage_id = stage_row['id']
                values = []
                for key in stage_row:
                    if key in ['id', 'creation_time', 'creation_user']:
                        continue
                    values.append(stage_row[key])

                data_list = []
                for data_block in values:
                    data_list.append(str(data_block))
                data = (' ').join(data_list)
                data = data.replace('assets','')
                data = data.replace('sequences','')

                for keywords_set in keywords_sets:
                    if keywords_set == '':
                        continue
                    keywords = keywords_set.split('&')
                    if all(keyword.upper() in data.upper() for keyword in keywords):
                        stages_to_show.append(stage_id)

            QtWidgets.QApplication.processEvents()
            time.sleep(0.1)
            for stage_row in self.stage_rows:
                if stage_row['id'] in stages_to_show:
                    self.show_stage_signal.emit(stage_row['id'])
                else:
                    self.hide_stage_signal.emit(stage_row['id'])

        except:
            logger.info(str(traceback.format_exc()))
        self.running = False