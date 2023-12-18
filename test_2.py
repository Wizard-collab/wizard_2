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

class calendar_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendar_widget, self).__init__(parent)

        self.resize(800, 600)

        self.header_view = test.calendar_header()
        self.view = test.calendar_viewport()

        self.init_users_images()
        self.build_ui()
        self.connect_functions()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 28, 12)
            self.users_images_dic[user_row['user_name']] = pixmap

    def connect_functions(self):
        self.view.scene_rect_update.connect(self.header_view.update_rect)
        self.view.scale_factor_update.connect(self.header_view.update_scale)
        self.view.zoom_factor_update.connect(self.header_view.update_zoom_factor)

    def build_ui(self):
        self.setObjectName('main_widget')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)

        self.main_layout.addWidget(self.header_view)
        self.main_layout.addWidget(self.view)

        for a in range(1):
            domains = project.get_domains()
            for category_row in project.get_domain_childs(domains[0]['id']):
                assets = project.get_category_childs(category_row['id'])
                for asset_row in assets:
                    stages = project.get_asset_childs(asset_row['id'])
                    for stage_row in stages:
                        item = stage_item(stage_row, datetime.datetime.fromtimestamp(stage_row['creation_time']),
                                            int(stage_row['estimated_time']/24),
                                            bg_color = ressources._stages_colors_[stage_row['name']],
                                            users_images_dic = self.users_images_dic)
                        self.view.add_item(item)

class stage_item(test.calendar_item):
    def __init__(self, stage_row, date, duration, bg_color, users_images_dic):
        super(stage_item, self).__init__(date=date, duration=duration, bg_color=bg_color)
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic

    def paint(self, painter, option, widget):
        super(stage_item, self).paint(painter, option, widget)
        rect = self.client_rect().toRect()
        margin = 2

        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawPixmap(rect.x()+margin, rect.y()+margin, self.users_images_dic[self.stage_row['assignment']])

        state_rect = QtCore.QRect(rect.x() + 28 + margin*2, rect.y() + margin, 4, rect.height()-margin*2)
        test.draw_rect(painter, state_rect, bg_color=QtGui.QColor(ressources._states_colors_[self.stage_row['state']]), radius=2)
        #test.draw_text(painter, state_rect, self.stage_row['state'], size=6)

        text_rect = QtCore.QRect(rect.x() + margin*4 + 4 + 28, rect.y(), 500, rect.height())
        zoom_factor = self.scene().zoom_factor
        stage_text = self.stage_row['string'].split('/')
        stage_text.pop(0)
        stage_text = f"{('/').join(stage_text)} - {int(self.duration)} day"
        test.draw_text(painter, text_rect, stage_text, size=12, align=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        


w= calendar_widget()
w.show()
