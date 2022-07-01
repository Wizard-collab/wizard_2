# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
import logging
import traceback

logger = logging.getLogger(__name__)


class pie_chart(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(pie_chart, self).__init__(parent)
        self.pies_list = []

    def add_pie(self, percent_factor=0, color='gray'):
        self.pies_list.append([percent_factor, color])

    def paintEvent(self, event):
        rectangle = QtCore.QRectF(0,0,self.width(), self.height())
        last_angle = 0
        painter = QtGui.QPainter(self)
        for pie in self.pies_list:
            painter.setPen(QtGui.QPen(QtGui.QColor(pie[1]), 0))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(pie[1]), QtCore.Qt.SolidPattern))
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
            angle = 360*pie[0]/100
            span_angle = int(angle*16)
            painter.drawPie(rectangle, last_angle, span_angle)
            last_angle += span_angle

class curves_chart(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(curves_chart, self).__init__(parent)
        self.lines = dict()
        self.ordonea_headers = []

    def add_line(self, data, color, thickness, name, style=QtCore.Qt.SolidLine):
        self.lines[name] = dict()
        self.lines[name]['data'] = data
        self.lines[name]['color'] = color
        self.lines[name]['thickness'] = thickness
        self.lines[name]['style'] = style

    def clear(self):
        self.lines = dict()

    def set_ordonea_headers(self, headers):
        self.ordonea_headers = headers

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        m = 30
        w = self.width()
        h = self.height()
        self.draw_grid(painter, m, w, h)
        self.draw_ordonea_headers(painter, m, w, h)
        for line in self.lines.keys():
            self.draw_line(self.lines[line], painter, m, w, h)

    def draw_line(self, line_dic, painter, m, w, h):
        line_margin = 10
        m += line_margin
        data_len = len(line_dic['data'])
        if data_len >= 2:
            old_point = None
            for point in line_dic['data']:
                if not old_point:
                    old_point = point
                else:
                    pen = QtGui.QPen()
                    pen.setBrush(QtGui.QColor(line_dic['color']))
                    pen.setWidth(line_dic['thickness'])
                    pen.setStyle(line_dic['style'])
                    pen.setCapStyle(QtCore.Qt.RoundCap)
                    pen.setJoinStyle(QtCore.Qt.RoundJoin)
                    painter.setPen(pen)
                    painter.drawLine(((w-m*2)*old_point[0])/100+m,
                                        h-(((h-m*2)*old_point[1])/100+m),
                                        ((w-m*2)*point[0])/100+m, 
                                        h-(((h-m*2)*point[1])/100+m))
                    old_point = point

    def draw_grid(self, painter, m, w, h):
        painter.setPen(QtGui.QPen(QtGui.QColor(255,255,255,10), 1))
        painter.drawLine(w/2, m, w/2, h-m)
        painter.drawLine((w-m*2)/4+m, m, (w-m*2)/4+m, h-m)
        painter.drawLine(((w-m*2)/4)*3+m, m, ((w-m*2)/4)*3+m, h-m)
        painter.drawLine(w-m, m, w-m, h-m)
        painter.drawLine(m, m, w-m, m)
        painter.drawLine(m, h/2, w-m, h/2)
        painter.drawLine(m, (h-m*2)/4+m, w-m, (h-m*2)/4+m)
        painter.drawLine(m, ((h-m*2)/4)*3+m, w-m, ((h-m*2)/4)*3+m)
        painter.setPen(QtGui.QPen(QtGui.QColor('gray'), 1))
        painter.drawLine(m, m, m, h-m)
        painter.drawLine(m, h-m, w-m, h-m)

    def draw_ordonea_headers(self, painter, m, w, h):
        painter.save()
        painter.setLayoutDirection(QtCore.Qt.RightToLeft)
        for header in self.ordonea_headers:
            font = QtGui.QFont()
            font_metric = QtGui.QFontMetrics(font)
            header_index = self.ordonea_headers.index(header)
            painter.drawText(m-font_metric.width(header), h-(h-m*2)*(header_index/(len(self.ordonea_headers)-1))-m, header)
        painter.restore()
