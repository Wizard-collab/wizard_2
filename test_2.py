import test
from wizard.gui import app_utils
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
import datetime
import time
import random
from wizard.core import project
from wizard.vars import ressources
from wizard.gui import gui_utils
from wizard.core import image
from wizard.core import repository

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

            self.priority_images_dic[priority] = pixmap

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)
        self.search_bar.textChanged.connect(self.update_search)
    def change_group_method(self):
        self.refresh()

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        self.group_label =  QtWidgets.QLabel('Group by')
        self.header_layout.addWidget(self.group_label)
        self.group_methods_comboBox = gui_utils.QComboBox()
        self.header_layout.addWidget(self.group_methods_comboBox)

        self.main_layout.addWidget(self.header_view)
        self.main_layout.addWidget(self.view)

    def update_search(self):
        if self.old_thread_id and self.old_thread_id in self.search_threads.keys():
        self.search_threads[thread_id].show_stage_signal.connect(self.show_stage)
        if len(search_data) > 0:
            self.accept_item_from_thread = True
            self.search_threads[thread_id].update_search(self.stage_rows, search_data)
    def refresh(self):

        self.grouped_dic = dict()
        self.grouped_dic['frames'] = dict()

        domains = project.get_domains()
        for domain_row in domains:
            if domain_row['name'] == 'library':
                continue
            for category_row in project.get_domain_childs(domain_row['id']):
                assets = project.get_category_childs(category_row['id'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    
                    for stage_row in stages:
                        
                        group_name = stage_row['name']
                        if group_name not in self.grouped_dic['frames'].keys():
                            self.grouped_dic['frames'][group_name] = dict()
                            self.grouped_dic['frames'][group_name]['items'] = []

                        item = stage_item(stage_row, datetime.datetime.fromtimestamp(stage_row['creation_time']),
                                            int(stage_row['estimated_time']/24),
                                            bg_color = ressources._stages_colors_[stage_row['name']],
                                            users_images_dic = self.users_images_dic)
                        self.grouped_dic['frames'][group_name]['items'].append(item)

        for group_name in self.grouped_dic['frames'].keys():
            frame = frame_item(group_name, '#1d1d23')
            frame.signal_manager.select.connect(self.select_frame_children)
            self.grouped_dic['frames'][group_name]['frame_item'] = frame
            self.view.add_frame(frame)

            for item in self.grouped_dic['frames'][group_name]['items']:
                self.view.add_item(item)
                item.stage_item_signal_manager.item_updated.connect(self.update_frames)
            
            self.update_frame_bouding_rect(group_name)

    def select_frame_children(self, group_name):
        if not group_name in self.grouped_dic['frames'].keys():
            return
        for item in self.grouped_dic['frames'][group_name]['items']:
            self.view.update_selection(item)

    def update_frame_bouding_rect(self, group_name):
        bounding_rect = self.grouped_dic['frames'][group_name]['items'][0].sceneBoundingRect()
        for item in self.grouped_dic['frames'][group_name]['items'][1:]:
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        self.grouped_dic['frames'][group_name]['frame_item'].update_rect(bounding_rect)

    def update_frames(self):
        for group_name in self.grouped_dic['frames'].keys():
             self.update_frame_bouding_rect(group_name)

class stage_item(test.calendar_item):
    def __init__(self, stage_row, date, duration, bg_color, users_images_dic):
        super(stage_item, self).__init__(date=date, duration=duration, bg_color=bg_color)
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic
        self.stage_item_signal_manager = signal_manager()

    def paint(self, painter, option, widget):
        super(stage_item, self).paint(painter, option, widget)
        if self.scene().zoom_factor > 0.15:
            rect = self.client_rect().toRect()
            margin = 2
            painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            painter.drawPixmap(rect.x()+margin, rect.y()+margin, self.users_images_dic[self.stage_row['assignment']])
            state_rect = QtCore.QRect(rect.x() + 28 + margin*2, rect.y() + margin, 4, rect.height()-margin*2)
            test.draw_rect(painter, state_rect, bg_color=QtGui.QColor(ressources._states_colors_[self.stage_row['state']]), radius=2)
        if self.scene().zoom_factor > 0.23:
            text_rect = QtCore.QRect(rect.x() + margin*4 + 4 + 28, rect.y(), 500, rect.height())
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
        self.margin = 10
        self.group_name = group_name
        self.setZValue(-1)

    def update_rect(self, rect):
        self.setPos(rect.x()-self.margin, rect.y()-self.margin)
        self.prepareGeometryChange()
        self.width = rect.width()+self.margin*2
        self.height = rect.height()+self.margin*2

    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.LeftButton:
            self.signal_manager.select.emit(self.group_name)
        else:
            super().mouseReleaseEvent(event)

