import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import test_calendar
import traceback

from wizard.gui import app_utils

from datetime import datetime, timedelta

start_date = datetime(2023, 10, 1)
end_date = datetime(2023, 11, 25)

# Create the application object
app = app_utils.get_app()

class calendarWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(calendarWidget, self).__init__(parent)
        self.display_type = 2
        self.dragging = False
        self.drag_start_x = 0
        self.start_date = start_date
        self.end_date = end_date
        self.items = []

    def add_item(self, date, duration, color, widget):
        item = item_object(date, duration, color, widget)
        self.items.append(item)

    def paintEvent(self, event):
        self.years_dic, self.months_dic, self.weeks_dic, self.days_dic = test_calendar.get_days_in_range(self.start_date, self.end_date)
        try:
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)

            self.position = 0
            self.main_area = QtCore.QRectF(0,0,self.width(), self.height())
            self.day_width = self.width()/len(self.days_dic.keys())
            self.draw_years()
            self.draw_months()
            self.draw_days()
            self.draw_weeks()
            self.draw_items()
            self.draw_current_day()
        except:
            print(str(traceback.format_exc()))

    def draw_items(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        first_day_dic = self.days_dic[list(self.days_dic.keys())[0]]
        first_day_id = list(self.days_dic.keys())[0]
        first_day_datetime = datetime(int(first_day_dic['year']),
                                        int(first_day_dic['month_number']),
                                        int(first_day_dic['day_number']))

        pos_y = self.years_section_height + self.month_section_height + self.day_section_height + self.weeks_section_height

        for item in self.items:
            date_id = item.date.strftime("%Y_%m_%W_%d")
            duration = item.duration
            if item.date < first_day_datetime:
                date_id = first_day_id
                duration = item.duration - (first_day_datetime - item.date).days
            end_date_id = (item.date + timedelta(days=item.duration)).strftime("%Y_%m_%W_%d")
            if date_id not in self.days_dic.keys() and end_date_id not in self.days_dic.keys():
                continue
            pos_x_1 = self.get_day_position(date_id)
            width = duration * self.day_width
            rectangle = QtCore.QRectF(pos_x_1,
                                    pos_y,
                                    width,
                                    30)
            self.draw_rect(painter, rectangle, bg_color=QtGui.QColor(item.color), radius=8)
            rectangle = rectangle.toRect()
            #item.widget.render(painter, QtCore.QPoint(rectangle.x(), rectangle.y()), QtGui.QRegion(rectangle))
            pos_y += 34

    def get_day_position(self, day_id):
        index = list(self.days_dic.keys()).index(day_id)
        pos_x = self.day_width*(index)
        return pos_x

    def draw_current_day(self):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        today_id = test_calendar.get_current_day_id()
        if today_id not in self.days_dic.keys():
            return
        rectangle = QtCore.QRectF(self.get_day_position(today_id), self.years_section_height + self.month_section_height, self.day_width, self.height())
        self.draw_rect(painter, rectangle, QtGui.QColor('transparent'), QtGui.QColor(255,255,255,70), 1, 4)
        if self.day_width<20:
            rectangle = QtCore.QRectF((self.get_day_position(today_id)+self.day_width/2)-10-4, self.years_section_height + self.month_section_height-4, 28, 28)
            self.draw_rect(painter, rectangle, QtGui.QColor('#52525c'), QtGui.QColor('transparent'), 1, 14)
            self.draw_text(painter, rectangle, self.days_dic[today_id]['day_number'], bold=True)

    def draw_text(self, painter, rectangle, text, color=QtGui.QColor(255,255,255,int(255*0.85)), size=12, bold=False, align=QtCore.Qt.AlignCenter):
        font = QtGui.QFont()
        font.setBold(bold)
        font.setPixelSize(size)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(color, 1))
        painter.drawText(rectangle, align, text)

    def draw_rect(self, painter, rectangle, bg_color, outline=QtGui.QColor('transparent'), outline_width=0, radius=0):
        painter.setPen(QtGui.QPen(outline, outline_width))
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.drawRoundedRect(rectangle, radius, radius)

    def draw_days(self):
        painter = QtGui.QPainter(self)
        draw_alternate_bg = 1
        for day_id in self.days_dic.keys():
            self.day_section_height = 0
            
            day_pos = self.get_day_position(day_id)
            number = self.days_dic[day_id]['day_number']
            name = self.days_dic[day_id]['day_name'][:3]

            rectangle = QtCore.QRectF(day_pos, self.years_section_height + self.month_section_height, self.day_width, self.height())
            self.draw_rect(painter, rectangle, bg_color=QtGui.QColor(0,0,0,10*draw_alternate_bg))

            if self.day_width > 20:
                text_color = QtGui.QColor(255,255,255,int(255*0.9))
                if name in ['Sat', 'Sun']:
                    text_color = QtGui.QColor(255,255,255,int(255*0.4))
                text_rect = QtCore.QRectF(day_pos,
                                        self.years_section_height + self.month_section_height,
                                        self.day_width,
                                        20)
                self.draw_text(painter, text_rect, number, text_color, 12, True)
                self.day_section_height += 20

            if self.day_width > 30:
                text_rect = QtCore.QRectF(day_pos,
                                    self.years_section_height + self.month_section_height + self.day_section_height,
                                    self.day_width,
                                    10)
                self.draw_text(painter, text_rect, name, QtGui.QColor(255,255,255,int(255*0.4)), 12, False)
                self.day_section_height += 10

            draw_alternate_bg = 1-draw_alternate_bg

    def draw_weeks(self):
        if self.day_width < 5:
            return
        painter = QtGui.QPainter(self)
        margin = 2
        weeks = list(self.weeks_dic.keys())
        
        for week in weeks:
            name = f"Week {week}"
            if self.day_width < 20:
                name = week
            days_range = self.weeks_dic[week]
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width
            rectangle = QtCore.QRectF(point_x_1 + margin,
                            self.years_section_height + self.month_section_height + self.day_section_height + margin,
                            point_x_2-point_x_1-margin*2,
                            20)
            self.draw_rect(painter, rectangle, bg_color=QtGui.QColor('#232329'), radius=4)
            self.draw_text(painter, rectangle, name)

        self.weeks_section_height = 30

    def draw_months(self):
        painter = QtGui.QPainter(self)
        margin = 2
        months = list(self.months_dic.keys())
        for month in months:
            days_range = self.months_dic[month]
            name = self.days_dic[days_range[0]]['month_name']
            if self.day_width < 2:
                name = name[:3]
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width

            rectangle = QtCore.QRectF(point_x_1 + margin, self.years_section_height+margin, point_x_2-point_x_1-margin*2, 25)
            self.draw_rect(painter, rectangle, bg_color=QtGui.QColor('#3d3d43'), radius=4)
            self.draw_text(painter, rectangle, name, size=15, bold=True)

        self.month_section_height = 29

    def draw_years(self):
        painter = QtGui.QPainter(self)
        margin = 10
        years = list(self.years_dic.keys())
        for year in years:
            days_range = self.years_dic[year]
            name = year
            point_x_1 = self.get_day_position(days_range[0])
            point_x_2 = self.get_day_position(days_range[-1]) + self.day_width
            rectangle = QtCore.QRectF(point_x_1 + margin, margin, point_x_2-point_x_1-margin*2, 40)
            self.draw_text(painter, rectangle, name, size=20, bold=True, align=QtCore.Qt.AlignLeft)
        self.years_section_height = 40

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.dragging = True
            self.drag_start_x = event.x()
        else:
            self.dragging = False

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.x() - self.drag_start_x
            # Update the start and end day based on the drag movement
            self.start_date -= timedelta(days=0.2*delta/(self.day_width/5))
            self.end_date -= timedelta(days=0.2*delta/(self.day_width/5))
            #self.start_day -= delta // self.column_width
            #self.end_day -= delta // self.column_width
            self.drag_start_x = event.x()
            self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.center_around_current_date()
            self.update()

    def center_around_current_date(self):
        current_date = datetime.today()
        days_to_center = len(self.days_dic.keys())/2
        self.start_date = (current_date - timedelta(days=days_to_center))
        self.end_date = (current_date + timedelta(days=days_to_center))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y() / 10  # Standard mouse wheel increment

            start_date = self.start_date + timedelta(days=1*delta/(self.day_width/10))
            end_date = self.end_date - timedelta(days=1*delta/(self.day_width/10))

            time_delta = end_date - start_date

            if time_delta.days < 8 or time_delta.days > 500:
                return
            self.start_date = start_date
            self.end_date = end_date
            self.update()

class item_object(QtCore.QObject):
    def __init__(self, date, duration, color, widget, parent=None):
        super(item_object, self).__init__(parent)
        self.date = date
        self.duration = duration
        self.color = color
        self.widget = widget

class widget_test(QtWidgets.QFrame):
    def __init__(self, text, parent=None):
        super(widget_test, self).__init__(parent)
        #self.setObjectName('transparent_widget')
        self.setStyleSheet("background-color:red")
        self.main_layout =QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.label = QtWidgets.QLabel(text)
        self.main_layout.addWidget(self.label)

w=calendarWidget()
w.show()
w.add_item(datetime(2023,10,30), 5, '#ff8666', widget_test("modeling"))
w.add_item(datetime(2023,10,24), 10, '#66a0ff', widget_test("Rigging"))
w.add_item(datetime(2023,9,24), 56, '#b7da62', widget_test("Animation"))
w.add_item(datetime(2023,10,21), 1, '#ff8666', widget_test("4"))




# Start the application event loop
sys.exit(app.exec_())