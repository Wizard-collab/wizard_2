# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal

class tag_label(QtWidgets.QWidget):

    enter = pyqtSignal(str)
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
        self.space_width = self.font_metric.width(' ')
        self.no_multiple_lines = False
        self.align_right = False
        self.stop_drawing = False
        self.tokens = []

    def setText(self, text):
        self.text = text
        self.parse_tokens()
        self.calculate_height()

    def resizeEvent(self, event):
        self.parse_tokens()
        self.calculate_height()

    def set_width(self):
        max_width = self.parent().maximumWidth()
        lines = self.text.split('\n')
        tokens = []
        larger = 0
        for line in lines:
            width = self.get_items_width(line.split())
            if width > larger:
                larger = width
        if larger > max_width:
            larger = max_width
        self.setMinimumWidth(larger)

    def calculate_height(self):
        heigth = (len(self.tokens)*self.font_height)+(len(self.tokens)*self.tag_block_margin)+self.tag_block_margin
        self.setMinimumHeight(heigth)

    def setNoMultipleLines(self, no_multiple_lines=True):
        self.no_multiple_lines = no_multiple_lines

    def setAlignRight(self, align_right=True):
        self.align_right = align_right

    def enterEvent(self, event):
        self.enter.emit(self.text)

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
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 0))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('#ffffff')))
        pos = [0, 0]
        pos[1] += self.font_height
        space_width = self.font_metric.width(' ')
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
        width = self.font_metric.width(item)
        if item.startswith('@'):
            width += self.tag_block_margin*2
        return width
                    
    def draw_item(self, item, pos, item_width, painter):
        if self.no_multiple_lines:
            if pos[0] + item_width > self.width():
                while (pos[0] + item_width + self.get_item_width('...') > self.width()) and len(item) >= 1:
                    item = item[:-1]
                    item_width = self.get_item_width(item)
                item += '...'
                item_width = self.get_item_width(item)
                self.stop_drawing = True

        if item.startswith('@'):
            pos_to_draw = [pos[0], pos[1]]
            painter.setBrush(QtGui.QBrush(QtGui.QColor(119, 133, 222, 255)))
            pen = QtGui.QPen()
            pen.setBrush(QtGui.QColor('transparent'))
            pen.setCapStyle(QtCore.Qt.RoundCap)
            pen.setJoinStyle(QtCore.Qt.RoundJoin)
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
