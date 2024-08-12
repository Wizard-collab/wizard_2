# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtProperty
import sys
import os
import logging

# Wizard modules
from wizard.vars import ressources

# Wizard gui modules
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

class QFlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None):
        super(QFlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(QFlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

def QIcon_from_svg(svg_filepath, color='black'):
    img = QtGui.QPixmap(svg_filepath)
    qp = QtGui.QPainter(img)
    qp.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_SourceIn)
    qp.fillRect( img.rect(), QtGui.QColor(color) )
    qp.end()
    return QtGui.QIcon(img)

def move_ui(widget, margin=0, pos=None):
    screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
    if not screen:
        screen = QtWidgets.QGuiApplication.primaryScreen()
    screenRect = screen.availableGeometry()

    screen_minX = screenRect.topLeft().x()
    screen_minY = screenRect.topLeft().y()
    screen_maxX = screenRect.bottomRight().x()
    screen_maxY = screenRect.bottomRight().y()
    if pos is None:
        cursor_x = QtGui.QCursor.pos().x()
        cursor_y = QtGui.QCursor.pos().y()
    else:
        cursor_x = pos.x()
        cursor_y = pos.y()
    win_width = widget.frameSize().width()
    win_heigth = widget.frameSize().height()

    if margin != 0:
        margin -= 15

    if (cursor_y - (30-margin*2) - win_heigth) <= screen_minY:
        posy = cursor_y - (15-margin)
        angley = 'top'
    else:
        posy = cursor_y - win_heigth + (15-margin)
        angley = 'bottom'
    if (cursor_x + (30-margin*2) + win_width) >= screen_maxX:
        posx = cursor_x - win_width + (15-margin)
        anglex = 'right'
    else:
        posx = cursor_x - (15-margin)
        anglex = 'left'

    widget.move(posx, posy)
    return f"{angley}-{anglex}"

def mask_image(imgdata, imgtype='png', size=64, custom_radius=None):
    image = QtGui.QImage.fromData(imgdata, imgtype)
    image.convertToFormat(QtGui.QImage.Format.Format_ARGB32)
    imgsize = min(image.width(), image.height())
    rect = QtCore.QRect(
        int((image.width() - imgsize) / 2),
        int((image.height() - imgsize) / 2),
        imgsize,
        imgsize,
    )
    image = image.copy(rect)
    out_img = QtGui.QImage(imgsize, imgsize, QtGui.QImage.Format.Format_ARGB32)
    out_img.fill(QtCore.Qt.GlobalColor.transparent)
    brush = QtGui.QBrush(image)        # Create texture brush
    painter = QtGui.QPainter(out_img)  # Paint the output image
    painter.setBrush(brush)      # Use the image texture brush
    painter.setPen(QtCore.Qt.PenStyle.NoPen)     # Don't draw an outline
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)  # Use AA
    if custom_radius:
        rect = QtCore.QRect(0,0,imgsize,imgsize)
        painter.drawRoundedRect(rect, custom_radius, custom_radius)
    else:
        painter.drawEllipse(0, 0, imgsize, imgsize)  # Actually draw the circle
    painter.end()                # We are done (segfault if you forget this)
    pr = QtGui.QWindow().devicePixelRatio()
    pm = QtGui.QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(int(size), int(size), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
    return pm
    
def round_corners_image_button(imgdata, size_tuple, radius, imgtype='png'):
    pr = QtGui.QWindow().devicePixelRatio()
    image = QtGui.QImage.fromData(imgdata, imgtype)
    image.convertToFormat(QtGui.QImage.Format.Format_ARGB32)
    image = image.scaled(int(size_tuple[0]*pr), int(size_tuple[1]*pr), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
    out_img = QtGui.QImage(int(size_tuple[0]*pr), int(size_tuple[1]*pr), QtGui.QImage.Format.Format_ARGB32)
    out_img.fill(QtCore.Qt.GlobalColor.transparent)
    brush = QtGui.QBrush(image)        # Create texture brush
    painter = QtGui.QPainter(out_img)  # Paint the output image
    painter.setBrush(brush)      # Use the image texture brush
    painter.setPen(QtCore.Qt.PenStyle.NoPen)     # Don't draw an outline
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)  # Use AA
    path = QtGui.QPainterPath()
    path.addRoundedRect(
        0, 0, int(size_tuple[0]*pr), int(size_tuple[1]*pr), int(radius*pr), int(radius*pr))
    painter.setClipPath(path)
    painter.drawPath(path)
    painter.end()                # We are done (segfault if you forget this)
    pm = QtGui.QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    return pm

class no_return_textEdit(QtWidgets.QTextEdit):

    apply_signal = pyqtSignal(int)

    def __init__(self, parent=None):
        super(no_return_textEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.key() == QtCore.Qt.Key.Key_Return:
                self.insertPlainText('\n')
                self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            else:
                super().keyPressEvent(event)
        else:
            if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
                self.apply_signal.emit(1)
            else:
                super().keyPressEvent(event)


class QComboBox(QtWidgets.QComboBox):
    def __init__(self, parent = None):
        super(QComboBox, self).__init__(parent)
        self.view().window().setWindowFlags(QtCore.Qt.WindowType.Popup | QtCore.Qt.WindowType.NoDropShadowWindowHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.view().window().setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.view().window().setStyleSheet("QListView::item:hover{background:#4b4b57;}QListView::item:selected{background:#4b4b57;}")
        self.setItemDelegate(QtWidgets.QStyledItemDelegate())

class QMenu(QtWidgets.QMenu):
    def __init__(self, parent = None):
        super(QMenu, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowType.Popup | QtCore.Qt.WindowType.NoDropShadowWindowHint | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QListView::item:hover{background:#4b4b57;}QListView::item:selected{background:#4b4b57;}")

class separator(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(separator, self).__init__(parent)
        self.setMinimumHeight(1)
        self.setMaximumHeight(1)
        self.setObjectName('separator')

class vertical_separator(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(vertical_separator, self).__init__(parent)
        self.setMinimumWidth(1)
        self.setMaximumWidth(1)
        self.setObjectName('separator')

class ElidedLabel(QtWidgets.QLabel):
    _width = _text = _elided = None

    def __init__(self, text='', width=40, parent=None):
        super(ElidedLabel, self).__init__(text, parent)
        self.setMinimumWidth(width if width > 0 else 1)

    def elidedText(self):
        return self._elided or ''

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.drawFrame(painter)
        margin = self.margin()
        rect = self.contentsRect()
        rect.adjust(margin, margin, -margin, -margin)
        text = self.text()
        width = rect.width()
        if text != self._text or width != self._width:
            self._text = text
            self._width = width
            self._elided = self.fontMetrics().elidedText(
                text, QtCore.Qt.TextElideMode.ElideRight, width)
        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        self.style().drawItemText(
            painter, rect, self.alignment(), option.palette,
            self.isEnabled(), self._elided, self.foregroundRole())

class QProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        super(QProgressBar, self).__init__(parent)

    def paintEvent(self, event):
        qp = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionProgressBar()
        self.initStyleOption(opt)
        rect = self.style().subElementRect(QtWidgets.QStyle.SubElement.SE_ProgressBarContents, opt, self)
        minSize = rect.height()
        grooveSize = rect.width() - minSize - 1
        valueRange = self.maximum() - self.minimum()
        offset = self.value() / valueRange * grooveSize
        newValue = (minSize + 1 + offset) / rect.width() * valueRange
        if int(newValue) != newValue:
            newValue = min(self.maximum(), newValue + 1)
        opt.progress = int(newValue)
        qp.drawControl(QtWidgets.QStyle.ControlElement.CE_ProgressBar, opt)

class QRightClickButton(QtWidgets.QPushButton):

    rightClicked = pyqtSignal(object)
    leftClicked = pyqtSignal(object)

    def __init__(self, parent=None):
        super(QRightClickButton, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.rightClicked.emit(1)
        else:
            self.leftClicked.emit(1)
        super().mouseReleaseEvent(event)

class password_lineEdit(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(password_lineEdit, self).__init__(parent)
        self.build_ui()
        self.connect_functions()
        self.toggle_password_visibility()

    def build_ui(self):
        self.setObjectName('password_lineEdit_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0,0,10,0)

        self.setLayout(self.main_layout)

        self.password_lineEdit = QtWidgets.QLineEdit()
        self.main_layout.addWidget(self.password_lineEdit)

        self.toggle_visibility_button = QtWidgets.QPushButton()
        self.toggle_visibility_button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.toggle_visibility_button.setObjectName('password_visibility_button')
        self.toggle_visibility_button.setIcon(QtGui.QIcon(ressources._password_visibility_on_))
        self.toggle_visibility_button.setCheckable(True)
        self.toggle_visibility_button.setFixedSize(16,16)
        self.toggle_visibility_button.setIconSize(QtCore.QSize(14,14))
        self.main_layout.addWidget(self.toggle_visibility_button)

    def connect_functions(self):
        self.toggle_visibility_button.clicked.connect(self.toggle_password_visibility)

    def toggle_password_visibility(self):
        if not self.toggle_visibility_button.isChecked():
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.toggle_visibility_button.setIcon(QtGui.QIcon(ressources._password_visibility_off_))
        else:
            self.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.toggle_visibility_button.setIcon(QtGui.QIcon(ressources._password_visibility_on_))

    def text(self):
        return self.password_lineEdit.text()

    def clear(self):
        self.password_lineEdit.clear()

    def setPlaceholderText(self, placeholderText):
        self.password_lineEdit.setPlaceholderText(placeholderText)

class search_bar(QtWidgets.QFrame):

    textChanged = pyqtSignal(str)

    def __init__(self, parent=None, red=44, green=44, blue=51, alpha=255):
        super(search_bar, self).__init__(parent)
        self.bg_color = QtGui.QColor(red, green, blue, alpha)
        self.build_ui()
        self.connect_functions()
        self.old_text=''
        self._set_color(self.bg_color)

    def build_ui(self):
        self.setObjectName('search_bar_frame')
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(8,4,8,4)
        self.main_layout.setSpacing(4)
        self.setLayout(self.main_layout)
        self.search_icon_label = QtWidgets.QLabel()
        self.search_icon_label.setPixmap(QtGui.QIcon(ressources._search_icon_).pixmap(18))
        self.main_layout.addWidget(self.search_icon_label)
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setObjectName("search_lineEdit")
        self.main_layout.addWidget(self.search_bar)
        self.clear_search_button = close_button()
        self.clear_search_button.setFixedSize(16,16)
        self.clear_search_button.setIconSize(QtCore.QSize(12,12))
        self.clear_search_button.setObjectName('clear_search_button')
        self.clear_search_button.setVisible(0)
        self.main_layout.addWidget(self.clear_search_button)

    def setPlaceholderText(self, placeholderText):
        self.search_bar.setPlaceholderText(placeholderText)

    def text(self):
        return self.search_bar.text()

    def setText(self, text):
        self.search_bar.setText(text)

    def connect_functions(self):
        self.search_bar.textChanged.connect(self.textChanged.emit)
        self.search_bar.textChanged.connect(self.text_changed)
        self.clear_search_button.clicked.connect(self.search_bar.clear)

    def keyPressEvent(self, event):
        self.search_bar.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.search_bar.keyReleaseEvent(event)

    def setFocus(self, value):
        self.search_bar.setFocus(value)

    def text_changed(self, text):
        self.update_clear_button(text)
        self.update_bg(text)

    def _set_color(self, color):
        self.setStyleSheet('#search_bar_frame{background-color:rgba(%s, %s, %s, %s);}' % (color.red() ,
                                                                                                color.green(),
                                                                                                color.blue(), 
                                                                                                color.alpha()))

    def update_bg(self, text):
        if text == '' and self.old_text!='':
            self.anim = QtCore.QPropertyAnimation(self, b"color")
            self.anim.setDuration(200)
            self.anim.setStartValue(QtGui.QColor(119, 133, 222, 255))
            self.anim.setEndValue(self.bg_color)
            self.anim.start()
        elif text != '' and self.old_text == '':
            self.anim = QtCore.QPropertyAnimation(self, b"color")
            self.anim.setDuration(200)
            self.anim.setStartValue(self.bg_color)
            self.anim.setEndValue(QtGui.QColor(119, 133, 222, 255))
            self.anim.start()
        self.old_text = text

    def update_clear_button(self, text):
        if text == '':
            self.clear_search_button.setVisible(False)
        else:
            self.clear_search_button.setVisible(True)

    color = pyqtProperty(QtGui.QColor, fset=_set_color)

class ScrollLabel(QtWidgets.QScrollArea):
 
    def __init__(self, *args, **kwargs):
        QtWidgets.QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QtWidgets.QWidget(self)
        self.setWidget(content)
        lay = QtWidgets.QVBoxLayout(content)
        lay.setContentsMargins(0,0,0,0)
        self.label = QtWidgets.QLabel(content)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)
 
    def setText(self, text):
        self.label.setText(text)

class close_button(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(close_button, self).__init__(parent)
        self.setIcon(QtGui.QIcon(ressources._close_tranparent_icon_))

    def enterEvent(self, event):
        self.setIcon(QtGui.QIcon(ressources._close_icon_))

    def leaveEvent(self, event):
        self.setIcon(QtGui.QIcon(ressources._close_tranparent_icon_))


class RoundProgress(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(RoundProgress, self).__init__(parent)
        self.chunck_color = '#d9d9d9'
        self.bg_color = '#24242b'
        self.percent=0
        self.line_width=18
 
    def setValue(self, percent):
        self.percent=percent
        self.update()

    def set_line_width(self, line_width):
        self.line_width=line_width
        self.update()

    def setChunckColor(self, color):
        self.chunck_color = color
        self.update()

    def paintEvent(self,event):
        rect=QtCore.QRectF(self.line_width/2,
                            self.line_width/2,
                            self.width()-self.line_width,
                            self.height()-self.line_width)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        # Draw bg
        self.draw_arc(painter, 0, 360, self.bg_color)
        # Draw chunck
        self.draw_arc(painter, 90, -360*(self.percent/100), self.chunck_color)

    def find_ellipse_coord(self, rect, start_angle, angle):
        coord_path = QtGui.QPainterPath()
        coord_path.arcMoveTo(rect, start_angle)
        coord_path.arcTo(rect, start_angle, angle)
        return coord_path.currentPosition()

    def draw_arc(self, painter, start_angle, angle, color):
        outer_rect = QtCore.QRectF(0,0,self.width(), self.height())
        inner_rect = QtCore.QRectF(self.line_width, self.line_width,   
                          self.width() - self.line_width*2, self.height() - self.line_width*2)
        path = QtGui.QPainterPath()
        path.arcMoveTo(outer_rect, start_angle)
        path.arcTo(outer_rect, start_angle, angle)
        path.lineTo(self.find_ellipse_coord(inner_rect, start_angle, angle))
        path.arcTo(inner_rect, start_angle+angle, -angle)
        path.lineTo(self.find_ellipse_coord(outer_rect, -angle, start_angle+angle))
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(color)))

def enterEvent(self, event=None):
    gui_server.tooltip(self.application_tooltip)
    self.legacy_enterEvent(event)

def leaveEvent(self, event=None):
    gui_server.tooltip('Tooltips')
    self.legacy_leaveEvent(event)

def application_tooltip(widget, custom_tooltip):
    widget.legacy_enterEvent = widget.enterEvent
    widget.application_tooltip = custom_tooltip
    widget.enterEvent = lambda self: enterEvent(widget)
    widget.legacy_leaveEvent = widget.leaveEvent
    widget.leaveEvent = lambda self: leaveEvent(widget)

def modify_application_tooltip(widget, custom_tooltip):
    widget.application_tooltip = custom_tooltip

def add_menu_to_menu_bar(menu_bar, title, icon=None):
    if icon is not None:
        menu = menu_bar.addMenu(icon, title)
    else:
        menu = menu_bar.addMenu(title)
    menu.setWindowFlags(QtCore.Qt.WindowType.Popup | QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.NoDropShadowWindowHint)
    menu.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
    return menu

class info_widget(QtWidgets.QFrame):

    customContextMenuRequested = pyqtSignal(int)

    def __init__(self, parent=None, transparent = None):
        super(info_widget, self).__init__(parent)
        self.transparent = transparent
        self.build_ui()

    def build_ui(self):
        self.setObjectName('dark_widget')
        if self.transparent:
            self.setObjectName('transparent_widget')
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(6)
        self.main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.main_layout)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

        self.image = QtWidgets.QLabel()
        self.image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.image)
        self.text = QtWidgets.QLabel()
        self.text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.text.setObjectName('title_label_gray')
        self.main_layout.addWidget(self.text)

        self.main_layout.addSpacerItem(QtWidgets.QSpacerItem(0,0, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding))

    def setImage(self, image):
        self.image.setPixmap(QtGui.QIcon(image).pixmap(200))

    def setText(self, text):
        self.text.setText(text)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            self.customContextMenuRequested.emit(1)

class transparent_button(QtWidgets.QPushButton):
    def __init__(self, icon, hover_icon, checked_icon=None, parent=None):
        super(transparent_button, self).__init__(parent)
        self.is_hover = False
        self.icon = icon
        self.hover_icon = hover_icon
        self.checked_icon = checked_icon
        self.non_checked_icon = icon
        self.setIcon(QtGui.QIcon(self.icon))
        self.reset_stylesheet()
        self.toggled.connect(self.check_update)

    def update_icon(self):
        if self.isCheckable():
            self.setIcon(QtGui.QIcon(self.icon))
            return
        if self.is_hover:
            self.setIcon(QtGui.QIcon(self.hover_icon))
        else:
            self.setIcon(QtGui.QIcon(self.icon))

    def check_update(self):
        if self.isChecked() and self.checked_icon is not None:
            self.icon = self.checked_icon
        else:
            self.icon = self.non_checked_icon
        self.update_icon()

    def enterEvent(self, event):
        self.is_hover = True
        self.update_icon()

    def leaveEvent(self, event):
        self.is_hover = False
        self.update_icon()

    def reset_stylesheet(self):
        self.setStyleSheet('background-color: transparent;border: none;')

class minimum_height_textEdit(QtWidgets.QTextEdit):
    def __init__(self, max_height=100, parent=None):
        super(minimum_height_textEdit, self).__init__(parent)
        self.max_height = max_height
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.connect_functions()
        self.update_height()

    def set_max_height(self, max_height):
        self.max_height = max_height
        self.update_height()

    def connect_functions(self):
        self.textChanged.connect(self.update_height)

    def showEvent(self, event):
        self.update_height()

    def update_height(self):
        doc_height = self.document().size().height() + 8
        if int(doc_height) > self.max_height:
            doc_height = self.max_height
        self.setMinimumHeight(int(doc_height))
        self.setMaximumHeight(int(doc_height))

class QSplitter(QtWidgets.QSplitter):
    def __init__(self, parent=None):
        super(QSplitter, self).__init__(parent)

    def createHandle(self):
        return QSplitterHandle(self.orientation(), self)

class QSplitterHandle(QtWidgets.QSplitterHandle):

    def __init__(self, orientation, parent):
        super(QSplitterHandle, self).__init__(orientation, parent)
        self.hovered = False
        self.pressed = False

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.pressed = False
        self.update()

    def mousePressEvent(self, event):
        self.pressed = True
        self.update()

    def mouseReleaseEvent(self, event):
        self.pressed = False
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.hovered and not self.pressed:
            painter.fillRect(self.rect(), QtGui.QColor(245,245,255,30))
        elif self.pressed:
            painter.fillRect(self.rect(), QtGui.QColor(0,0,10,30))
        else:
            painter.fillRect(self.rect(), QtGui.QColor("#292930"))

class GlobalClickDetector(QtCore.QObject):

    clicked_outside = pyqtSignal(int)
    clicked_inside = pyqtSignal(int)

    def __init__(self, target_widget, parent=None):
        super().__init__(parent)
        self.target_widget = target_widget

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            global_pos = event.globalPosition()
            target_global_geometry = self.target_widget.mapToGlobal(self.target_widget.rect().topLeft())
            target_global_rect = self.target_widget.rect().translated(target_global_geometry)

            if not target_global_rect.contains(global_pos.toPoint()):
                self.clicked_outside.emit(1)
            else:
                self.clicked_inside.emit(1)
        return super().eventFilter(obj, event)