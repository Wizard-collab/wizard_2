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

    def paintEvent(self, event):
        try:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

            m = 20
            w = self.width()
            h = self.height()

            # Draw grid
            painter.setPen(QtGui.QPen(QtGui.QColor(255,255,255,10), 1))
            painter.drawLine(w/2, m, w/2, h-m)
            painter.drawLine((w-m*2)/4+m, m, (w-m*2)/4+m, h-m)
            painter.drawLine(((w-m*2)/4)*3+m, m, ((w-m*2)/4)*3+m, h-m)
            painter.drawLine(w-m, m, w-m, h-m)

            painter.drawLine(m, m, w-m, m)
            painter.drawLine(m, h/2, w-m, h/2)
            painter.drawLine(m, (h-m*2)/4+m, w-m, (h-m*2)/4+m)
            painter.drawLine(m, ((h-m*2)/4)*3+m, w-m, ((h-m*2)/4)*3+m)

            # Ordinate
            painter.setPen(QtGui.QPen(QtGui.QColor('gray'), 1))
            painter.drawLine(m, m, m, h-m)

            # Abscissa
            painter.drawLine(m, h-m, w-m, h-m)

        except:
            logger.error(str(traceback.format_exc()))