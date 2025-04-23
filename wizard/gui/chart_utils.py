# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets
from PyQt6 import QtGui
from PyQt6 import QtCore
import sys
import time
import logging
import traceback

logger = logging.getLogger(__name__)


class pie_chart(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(pie_chart, self).__init__(parent)
        self.pies_list = []

    def add_pie(self, percent_factor=0, color='gray'):
        self.pies_list.append([percent_factor, color])
        self.update()

    def clear(self):
        self.pies_list = []
        self.update()

    def paintEvent(self, event):
        rectangle = QtCore.QRectF(0, 0, self.width(), self.height())
        last_angle = 0
        painter = QtGui.QPainter(self)
        for pie in self.pies_list:
            painter.setPen(QtGui.QPen(QtGui.QColor(pie[1]), 0))
            painter.setBrush(QtGui.QBrush(QtGui.QColor(
                pie[1]), QtCore.Qt.BrushStyle.SolidPattern))
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            angle = 360*pie[0]/100
            span_angle = int(angle*16)
            painter.drawPie(rectangle, last_angle, span_angle)
            last_angle += span_angle


class time_left_chart(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(time_left_chart, self).__init__(parent)
        self.setMinimumHeight(35)
        self.refresh(time.time(), time.time()+200)

    def refresh(self, project_creation_time, deadline):
        self.project_creation_time = project_creation_time
        self.deadline = deadline
        self.update()

    def paintEvent(self, event):
        rectangle = QtCore.QRectF(0, 0, self.width(), self.height())
        time_range = self.deadline - self.project_creation_time
        current_time = time.time() - self.project_creation_time
        percent = current_time/time_range*100
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 0))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('#d7d7d7'),
                         QtCore.Qt.BrushStyle.SolidPattern))
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        # Draw gradient
        gradient_line_rect = QtCore.QRectF(
            0, (self.height()/2)-3, self.width(), 6)
        path = QtGui.QPainterPath()
        path.addRoundedRect(gradient_line_rect, 3, 3)
        gradient = QtGui.QLinearGradient(
            gradient_line_rect.topLeft(), gradient_line_rect.topRight())
        gradient.setColorAt(0, QtGui.QColor('transparent'))
        gradient.setColorAt(percent/100, QtGui.QColor('#d7d7d7'))
        gradient.setColorAt(1, QtGui.QColor('#d7d7d7'))
        painter.fillPath(path, gradient)
        # Draw pointer
        position_x = (self.width()*percent/100) - 2
        position_y = (self.height()/2) - 20
        position_rect = QtCore.QRectF(position_x, position_y, 4, 12)
        path = QtGui.QPainterPath()
        path.addRoundedRect(position_rect, 2, 2)
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(
            '#d7d7d7'), QtCore.Qt.BrushStyle.SolidPattern))
        # Draw percent text
        text = f"{int(percent)} %"
        font = QtGui.QFont()
        font_metric = QtGui.QFontMetrics(font)
        width = font_metric.horizontalAdvance(text)
        height = font_metric.height()
        text_point_x = (self.width()*percent/100) - width/2
        text_point_y = self.height()/2 + height + 2
        if text_point_x <= 0:
            text_point_x = 0
        if text_point_x+width >= self.width():
            text_point_x = self.width() - width
        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 1))
        painter.drawText(int(text_point_x), int(text_point_y), text)


class curves_chart(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(curves_chart, self).__init__(parent)
        self.setMouseTracking(True)
        self.lines = dict()
        self.margin = 30
        self.prevision_visibility = True
        self.point_thickness = 5
        self.ordonea_headers = []
        self.abscissa_headers = []

    def add_line(self, data, color, thickness, name, style=QtCore.Qt.PenStyle.SolidLine):
        self.lines[name] = dict()
        self.lines[name]['data'] = data
        self.lines[name]['color'] = color
        self.lines[name]['thickness'] = thickness
        self.lines[name]['style'] = style
        self.lines[name]['name'] = name
        self.lines[name]['visibility'] = True

    def set_data_visible(self, data, visibility):
        if data in self.lines.keys():
            self.lines[data]['visibility'] = visibility
        self.update()

    def set_prevision_visibility(self, visibility):
        self.prevision_visibility = visibility
        self.update()

    def clear(self):
        self.lines = dict()

    def set_points_thickness(self, thickness=5):
        self.point_thickness = thickness

    def set_margin(self, margin=30):
        self.margin = margin

    def set_ordonea_headers(self, headers):
        self.ordonea_headers = headers

    def set_abscissa_headers(self, headers):
        self.abscissa_headers = headers

    def paintEvent(self, event):
        mouse = QtCore.QPoint(self.mapFromGlobal(QtGui.QCursor.pos()))
        mouseRect = QtCore.QRectF(mouse.x()-3, mouse.y()-3, 6, 6)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        self.draw_grid(painter, w, h)
        self.draw_ordonea_headers(painter, w, h)
        self.draw_abscissa_headers(painter, w, h)
        for line in self.lines.keys():
            self.draw_line(self.lines[line], painter, w, h, mouseRect)
        for line in self.lines.keys():
            self.check_tip(self.lines[line], painter, mouseRect, mouse)

    def mouseMoveEvent(self, event):
        self.update()
        super().mouseMoveEvent(event)

    def draw_line(self, line_dic, painter, w, h, mouseRect):
        data_len = len(line_dic['data'])
        if line_dic['visibility']:
            if data_len >= 2:
                old_point = None
                pen = QtGui.QPen()
                color = QtGui.QColor(line_dic['color'])
                pen.setBrush(color)
                pen.setStyle(line_dic['style'])
                pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
                pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
                path = QtGui.QPainterPath()
                first_point = line_dic['data'][0]
                for point in line_dic['data']:
                    point_x = ((w-self.margin*2)*point[0])/100+self.margin
                    point_y = h-(((h-self.margin*2)*point[1])/100+self.margin)
                    if not old_point:
                        old_point = point
                    else:
                        old_point_x = (w-self.margin*2) * \
                            old_point[0]/100+self.margin
                        old_point_y = h - \
                            (((h-self.margin*2)*old_point[1])/100+self.margin)
                        path.moveTo(old_point_x, old_point_y)
                        path.lineTo(point_x, point_y)
                        if self.point_thickness > 0:
                            pen.setWidth(self.point_thickness)
                            painter.setPen(pen)
                            painter.drawPoint(int(point_x), int(point_y))
                        old_point = point
                last_point = point

                pen.setWidth(line_dic['thickness'])
                painter.setPen(pen)
                painter.drawPath(path)
                line_dic['path'] = path

                if self.prevision_visibility:
                    if (last_point[0]-first_point[0]) != 0:
                        prevision_at_100_time = (
                            last_point[1]-first_point[1])/(last_point[0]-first_point[0])*100
                        prevision_time_at_100 = 100
                        if prevision_at_100_time > 100:
                            prevision_time_at_100 = (
                                100/prevision_at_100_time)*100 + first_point[0]
                            prevision_at_100_time = 100
                        last_point_x = ((w-self.margin*2) *
                                        last_point[0])/100+self.margin
                        last_point_y = h - \
                            (((h-self.margin*2)*last_point[1])/100+self.margin)
                        point_x = ((w-self.margin*2) *
                                   prevision_time_at_100)/100+self.margin
                        point_y = h - \
                            (((h-self.margin*2)*prevision_at_100_time)/100+self.margin)
                        color.setAlpha(100)
                        pen.setStyle(QtCore.Qt.PenStyle.DotLine)
                        pen.setBrush(color)
                        painter.setPen(pen)
                        path = QtGui.QPainterPath()
                        path.moveTo(int(last_point_x), int(last_point_y))
                        path.lineTo(int(point_x), int(point_y))
                        painter.drawPath(path)
                        line_dic['prevision_path'] = path

    def check_tip(self, line_dic, painter, mouseRect, mouse):
        if line_dic['visibility']:
            if 'path' in line_dic.keys():
                if line_dic['path'].intersects(mouseRect):
                    self.draw_tip(mouse, line_dic, painter)
            if self.prevision_visibility:
                if 'prevision_path' in line_dic.keys():
                    if line_dic['prevision_path'].intersects(mouseRect):
                        self.draw_tip(mouse, line_dic, painter, projection=1)

    def draw_tip(self, point, line_dic, painter, projection=0):
        if point.x() <= 0+self.margin:
            point.setX(self.margin)
        if point.x() >= self.width() - self.margin:
            point.setX(self.width() - self.margin)
        if point.y() <= 0+self.margin:
            point.setY(self.margin)
        if point.y() >= self.height() - self.margin:
            point.setY(self.height() - self.margin)
        pen_width = 4
        pen = QtGui.QPen()
        color = QtGui.QColor(line_dic['color'])
        pen.setBrush(color)
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush(color))

        height = self.height()-2*self.margin
        point_y = point.y()-self.margin
        progress = (height-point_y)/height*100
        if progress > 100:
            progress = 100
        if progress < 0:
            progress = 0

        if not projection:
            text = f"{line_dic['name']} {int(progress)}%"
        else:
            text = f"{line_dic['name']} projection: {int(progress)}%"

        margin = 3
        font = QtGui.QFont()
        font_metric = QtGui.QFontMetrics(font)

        width = font_metric.horizontalAdvance(text)
        height = font_metric.height()
        text_point_x = point.x() - width/2
        text_point_y = point.y() + height/2 - margin - 25
        point_x = point.x() - width/2 - margin
        point_y = point.y()-margin-height/2-25

        if point_x <= 0:
            point_x = 0 + pen_width
            text_point_x = margin + pen_width
        if point_x+width+margin*2 >= self.width():
            point_x = self.width() - width - margin*2 - pen_width
            text_point_x = point_x + margin
        if point_y <= 0:
            point_y = 0 + pen_width
            text_point_y = margin*2 + height/2 + pen_width

        rect = QtCore.QRectF(point_x, point_y, width+2*margin, height+2*margin)
        painter.drawRect(rect)

        painter.setPen(QtGui.QPen(QtGui.QColor('#d7d7d7'), 1))
        painter.drawText(int(text_point_x), int(text_point_y), text)

        painter.setPen(QtGui.QPen(QtGui.QColor('gray'),
                       1, QtCore.Qt.PenStyle.DashLine))
        painter.drawLine(int(point.x()), int(point.y()), int(
            point.x()), int(self.height()-self.margin))

        pen = QtGui.QPen()
        pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
        pen.setWidth(12)
        pen.setBrush(QtGui.QColor(line_dic['color']))
        painter.setPen(pen)
        painter.drawPoint(point)

    def draw_grid(self, painter, w, h):
        painter.setPen(QtGui.QPen(QtGui.QColor('gray'), 2))
        painter.drawLine(self.margin, self.margin, self.margin, h-self.margin)
        painter.drawLine(self.margin, h-self.margin,
                         w-self.margin, h-self.margin)

    def draw_ordonea_headers(self, painter, w, h):
        font = QtGui.QFont()
        font_metric = QtGui.QFontMetrics(font)
        header_index = 0
        for header in self.ordonea_headers:
            painter.setPen(QtGui.QPen(QtGui.QColor('gray'), 1))
            painter.drawText(int(self.margin-font_metric.horizontalAdvance(header)), int(
                h-(h-self.margin*2)*(header_index/(len(self.ordonea_headers)-1))-self.margin), header)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 10), 1))
            painter.drawLine(int(self.margin),
                             int(h-(h-self.margin*2)*(header_index /
                                 (len(self.ordonea_headers)-1))-self.margin),
                             int(w-self.margin),
                             int(h-(h-self.margin*2)*(header_index/(len(self.ordonea_headers)-1))-self.margin))
            header_index += 1

    def draw_abscissa_headers(self, painter, w, h):
        font = QtGui.QFont()
        font_metric = QtGui.QFontMetrics(font)
        header_index = 0
        for header in self.abscissa_headers:
            painter.setPen(QtGui.QPen(QtGui.QColor('gray'), 1))
            painter.drawText(int((w-self.margin*2)*(header_index/(len(self.abscissa_headers)-1))+self.margin-font_metric.horizontalAdvance(header)/2),
                             int(h-self.margin+font_metric.height()),
                             header)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 10), 1))
            painter.drawLine(int((w-self.margin*2)*(header_index/(len(self.abscissa_headers)-1))+self.margin),
                             int(self.margin),
                             int((w-self.margin*2)*(header_index /
                                 (len(self.abscissa_headers)-1))+self.margin),
                             int(h-self.margin))
            header_index += 1
