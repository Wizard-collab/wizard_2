# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal

# Wizard core modules
from wizard.core import repository
from wizard.core import image

# Wizard gui modules
from wizard.gui import gui_utils

class tag_label(QtWidgets.QWidget):

    enter = pyqtSignal(int)
    leave = pyqtSignal(int)
    move_event = pyqtSignal(int)

    def __init__(self, text='', parent=None):
        super(tag_label, self).__init__(parent)
        self.setMouseTracking(True)
        self.text = text
        self.tag_block_margin = 3
        self.font = QtGui.QFont("Roboto", 8)
        self.font_metric = QtGui.QFontMetrics(self.font)
        self.font_height = self.font_metric.height()
        self.space_width = self.font_metric.horizontalAdvance(' ')
        self.no_multiple_lines = False
        self.align_right = False
        self.stop_drawing = False
        self.tokens = []

    def setText(self, text):
        if text is None:
            text = ''
        self.text = text
        self.parse_tokens()
        self.calculate_height()

    def resizeEvent(self, event):
        self.parse_tokens()
        self.calculate_height()

    def get_width(self):
        lines = self.text.split('\n')
        larger = 0
        for line in lines:
            width = self.get_items_width(line.split())
            if width > larger:
                larger = width
        return larger

    def calculate_height(self):
        heigth = (len(self.tokens)*self.font_height)+(len(self.tokens)*self.tag_block_margin)+self.tag_block_margin
        self.setMinimumHeight(heigth)

    def setNoMultipleLines(self, no_multiple_lines=True):
        self.no_multiple_lines = no_multiple_lines

    def setAlignRight(self, align_right=True):
        self.align_right = align_right

    def enterEvent(self, event):
        self.enter.emit(1)

    def leaveEvent(self, event):
        self.leave.emit(1)

    def mouseMoveEvent(self, event):
        self.move_event.emit(1)
        super().mouseMoveEvent(event)

    def parse_tokens(self):
        # Parsing tokens
        index = 0
        self.tokens = []
        if self.no_multiple_lines:
            self.tokens = [self.text.split()]
            return
        lines = self.text.split('\n')
        for line in lines:
            self.tokens.append(line.split())
        for items in self.tokens:
            new_line = []
            if len(items) > 1:
                while (self.get_items_width(items) > self.width()) and len(items) > 1:
                    new_line.insert(0, items[-1])
                    items = items[:-1]
            if len(items) == 1:
                new_item = ''
                while (self.get_item_width(items[0]) > self.width()) and len(items[0]) > 1:
                    new_item = items[0][-1] + new_item
                    items[0] = items[0][:-1]
                if new_item != '':
                    new_line.insert(0, ('').join(new_item))
            self.tokens[index] = items
            if new_line != []:
                self.tokens.insert(index+1, new_line)
            index += 1

    def paintEvent(self, event):
        # Init painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 0))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('#ffffff')))
        pos = [0, 0]
        pos[1] += self.font_height
        space_width = self.font_metric.horizontalAdvance(' ')
        painter.setFont(self.font)
        
        # Draw tokens
        for line in self.tokens:
            if self.align_right and not self.no_multiple_lines:
                pos[0] = self.width() - self.get_items_width(line)
            for item in line:
                item_width = self.get_item_width(item)
                pos = self.draw_item(item, pos, item_width, painter)
                if self.stop_drawing and self.no_multiple_lines:
                    self.stop_drawing = False
                    break
                pos = self.draw_item(' ', pos, self.space_width, painter)
            self.new_line(pos)

    def new_line(self, pos):
        if self.no_multiple_lines:
            return pos
        pos[1] += self.font_height + self.tag_block_margin
        pos[0] = 0
        return pos

    def get_items_width(self, items):
        width = 0
        for item in items:
            width += self.get_item_width(item)
            width += self.get_item_width(' ')
        return width - self.get_item_width(' ')

    def get_item_width(self, item):
        width = self.font_metric.horizontalAdvance(item)
        if item.startswith('@'):
            width += self.tag_block_margin*2
        return width
                    
    def draw_item(self, item, pos, item_width, painter):
        if item.startswith('@'):
            pos_to_draw = [pos[0], pos[1]]
            painter.setBrush(QtGui.QBrush(QtGui.QColor(119, 133, 222, 100)))
            pen = QtGui.QPen()
            pen.setBrush(QtGui.QColor('transparent'))
            pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
            pen.setWidth(0)
            painter.setPen(pen)
            bouding_rect = self.font_metric.boundingRect(item)
            rect = QtCore.QRect((pos_to_draw[0]+bouding_rect.x()),
                                    (pos_to_draw[1]+bouding_rect.y())-self.tag_block_margin,
                                    (bouding_rect.width())+self.tag_block_margin*2,
                                    (bouding_rect.height())+self.tag_block_margin*2)
            painter.drawRoundedRect(rect, 3, 3)
            painter.setPen(QtGui.QPen(QtGui.QColor('white'), 0))
            pos_to_draw[0] += self.tag_block_margin
            painter.drawText(pos_to_draw[0], pos_to_draw[1], item)
        else:
            painter.drawText(pos[0], pos[1], item)
        pos[0] += item_width 
        return pos

class view_comment_widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(view_comment_widget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.ToolTip)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMaximumWidth(300)
        self.build_ui()
        self.init_users_images()

    def init_users_images(self):
        self.users_images_dic = dict()
        for user_row in repository.get_users_list():
            user_image =  user_row['profile_picture']
            pixmap = gui_utils.mask_image(image.convert_str_data_to_image_bytes(user_image), 'png', 18)
            self.users_images_dic[user_row['user_name']] = pixmap

    def build_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        self.main_widget_layout = QtWidgets.QHBoxLayout()
        self.main_widget_layout.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.main_widget_layout)

        self.main_widget = QtWidgets.QFrame()
        self.main_widget.setObjectName('black_round_frame')
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(6)
        self.main_widget.setLayout(self.main_layout)
        self.main_widget_layout.addWidget(self.main_widget)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setSpacing(6)
        self.main_layout.addLayout(self.header_layout)

        self.user_image_label = QtWidgets.QLabel()
        self.user_image_label.setFixedSize(18,18)
        self.header_layout.addWidget(self.user_image_label)

        self.user_name_label = QtWidgets.QLabel()
        self.user_name_label.setObjectName('gray_label')
        self.header_layout.addWidget(self.user_name_label)

        self.line_frame = QtWidgets.QFrame()
        self.line_frame.setFixedHeight(1)
        self.line_frame.setStyleSheet('background-color:rgba(255,255,255,20)')
        self.main_layout.addWidget(self.line_frame)

        self.content_label = tag_label()
        self.main_layout.addWidget(self.content_label)

    def show_comment(self, comment, user):
        if comment is not None and comment != '':
            self.content_label.setText(comment)
            self.user_name_label.setText(user)
            self.user_image_label.setPixmap(self.users_images_dic[user])
            width = self.content_label.get_width() + 24 + 22
            if width > self.maximumWidth():
                width = self.maximumWidth()
            self.setMinimumWidth(width)
            gui_utils.move_ui(self, 20)
            self.show()
            self.adjustSize()

    def move_ui(self):
        gui_utils.move_ui(self, 20)