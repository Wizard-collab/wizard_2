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

        self.view.set_zoom(0.5)

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
                    stage_items = []
                    for stage_row in stages:
                        item = stage_item(stage_row, datetime.datetime.fromtimestamp(stage_row['creation_time']),
                                            int(stage_row['estimated_time']/24),
                                            bg_color = ressources._stages_colors_[stage_row['name']],
                                            users_images_dic = self.users_images_dic)
                        stage_items.append(item)
                        self.view.add_item(item)

                    bounding_rect = stage_items[0].sceneBoundingRect()
                    for item in stage_items[1:]:
                        bounding_rect = bounding_rect.united(item.sceneBoundingRect())
                    frame_it = frame_item(asset_row, '#1d1d23')
                    frame_it.setZValue(-1)
                    frame_it.setPos(bounding_rect.x()-10, bounding_rect.y()-10)
                    frame_it.prepareGeometryChange()
                    frame_it.width = bounding_rect.width()+20
                    frame_it.height = bounding_rect.height()+20
                    self.view.add_frame(frame_it)


class stage_item(test.calendar_item):
    def __init__(self, stage_row, date, duration, bg_color, users_images_dic):
        super(stage_item, self).__init__(date=date, duration=duration, bg_color=bg_color)
        self.stage_row = stage_row
        self.users_images_dic = users_images_dic

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

class frame_item(test.frame_item):
    def __init__(self, asset_row, bg_color):
        super(frame_item, self).__init__(bg_color=bg_color)
        self.asset_row = asset_row

    def paint(self, painter, option, widget):
        super(frame_item, self).paint(painter, option, widget)
        
        rect = self.boundingRect().toRect()
        font = self.scene().font()
        font.setPixelSize(40)

        font_metrics = QtGui.QFontMetrics(font)
        text = self.asset_row['name']
        text_width = font_metrics.horizontalAdvance(text)
        text_rect = QtCore.QRect(rect.x() - 20 - text_width, rect.y(), 200, 50)
        test.draw_text(painter, text_rect, text, size=40, align=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

w= calendar_widget()
w.show()
