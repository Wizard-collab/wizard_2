# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets, QtCore, QtGui

class tag_label(QtWidgets.QWidget):
    def __init__(self, text='', parent=None):
        super(tag_label, self).__init__(parent)
        self.text = text
        self.tag_block_margin = 3
        self.font = QtGui.QFont("Roboto", 8)
        self.font_metric = QtGui.QFontMetrics(self.font)
        self.font_height = self.font_metric.height()
        self.space_width = self.font_metric.width(' ')
        self.no_multiple_lines = False

    def setText(self, text):
        self.text = text
        self.calculate_size()

    def resizeEvent(self, event):
        self.calculate_size()

    def calculate_size(self):
        pos = [0, 0]
        pos[1] += self.font_height
        start=1
        for line in self.text.split('\n'):
            if not start:
                pos = self.new_line(pos)
            start=0
            for word in line.split(' '):
                item_width = self.font_metric.width(word)
                if item_width >= self.width():
                    for letter in word:
                        item_width = self.font_metric.width(letter)
                        pos = self.get_pos(letter, pos, item_width)
                else:
                    pos = self.get_pos(word, pos, item_width)
                    pos = self.get_pos(' ', pos, self.space_width)
        self.setMinimumHeight(pos[1]+self.tag_block_margin*2)

    def get_pos(self, item, pos, item_width):
        if item != ' ':
            if pos[0]+item_width >= self.width():
                pos = self.new_line(pos)
        if item.startswith('@'):
            pos[0] += self.tag_block_margin + 4
        pos[0] += item_width 
        return pos

    def setNoMultipleLines(self, no_multiple_lines=True):
        self.no_multiple_lines = no_multiple_lines

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 0))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('#ffffff')))
        pos = [0, 0]
        pos[1] += self.font_height
        space_width = self.font_metric.width(' ')
        painter.setFont(self.font)
        start=1
        for line in self.text.split('\n'):
            if not start:
                self.new_line(pos)
            start=0
            for word in line.split(' '):
                item_width = self.font_metric.width(word)
                if item_width >= self.width():
                    for letter in word:
                        item_width = self.font_metric.width(letter)
                        pos = self.draw_item(letter, pos, item_width, painter)
                else:
                    pos = self.draw_item(word, pos, item_width, painter)
                    pos = self.draw_item(' ', pos, self.space_width, painter)

    def new_line(self, pos):
        if self.no_multiple_lines:
            return pos
        pos[1] += self.font_height + self.tag_block_margin
        pos[0] = 0
        return pos
                    
    def draw_item(self, item, pos, item_width, painter):
        if item != ' ':
            if pos[0] + item_width >= self.width():
                self.new_line(pos)
        if item.startswith('@'):
            pos[0] += 2
            painter.setBrush(QtGui.QBrush(QtGui.QColor(119, 133, 222, 255)))
            pen = QtGui.QPen()
            pen.setBrush(QtGui.QColor('transparent'))
            pen.setCapStyle(QtCore.Qt.RoundCap)
            pen.setJoinStyle(QtCore.Qt.RoundJoin)
            pen.setWidth(0)
            painter.setPen(pen)

            bouding_rect = self.font_metric.boundingRect(item)
            rect = QtCore.QRect((pos[0]+bouding_rect.x()),
                                    (pos[1]+bouding_rect.y())-self.tag_block_margin,
                                    (bouding_rect.width())+self.tag_block_margin*2,
                                    (bouding_rect.height())+self.tag_block_margin*2)
            painter.drawRoundedRect(rect, 3, 3)
            painter.setPen(QtGui.QPen(QtGui.QColor('white'), 0))
            pos[0] += self.tag_block_margin
        painter.drawText(pos[0], pos[1], item)
        if item.startswith('@'):
            pos[0] += self.tag_block_margin + 2
        pos[0] += item_width 
        return pos
