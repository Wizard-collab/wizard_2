# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.Qsci import QsciScintilla
from PyQt6.Qsci import QsciLexerCustom
import re


class script_editor_widget(QsciScintilla):
    ARROW_MARKER_NUM = 8
    drop_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(script_editor_widget, self).__init__(parent)

        self.font = QtGui.QFont()
        self.font.setFamily('Consolas')
        self.font.setFixedPitch(True)
        self.font.setPointSize(9)

        self.bold_font = QtGui.QFont()
        self.bold_font.setFamily('Consolas')
        self.bold_font.setFixedPitch(True)
        self.bold_font.setPointSize(9)
        self.bold_font.setBold(1)

        self.setLexer(python_lexer(self))
        self.setUtf8(1)
        self.build()
        self.setAcceptDrops(False)

    def build(self):
        self.setFont(self.font)
        self.setMarginsFont(self.font)

        self.setIndentationGuides(True)
        self.setIndentationGuidesForegroundColor(QtGui.QColor("#24242b"))
        self.setIndentationGuidesBackgroundColor(QtGui.QColor("#24242b"))

        self.setTabWidth(4)
        self.setAutoIndent(True)
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.setWrapIndentMode(QsciScintilla.WrapIndentMode.WrapIndentIndented)
        self.setSelectionBackgroundColor(QtGui.QColor("#7e7e91"))

        fontmetrics = QtGui.QFontMetrics(self.font)
        self.setMarginsFont(self.font)
        self.setMarginWidth(0, fontmetrics.horizontalAdvance("00000"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#292930"))
        self.setMarginsForegroundColor(QtGui.QColor("gray"))

        self.setMarginSensitivity(1, True)
        self.markerDefine(QsciScintilla.MarkerSymbol.RightArrow,
                          self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QtGui.QColor("#ffffff"),
                                      self.ARROW_MARKER_NUM)

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#292930"))
        self.setCaretForegroundColor(QtGui.QColor("#ffffff"))
        self.setMatchedBraceBackgroundColor(QtGui.QColor("#353540"))
        self.setMatchedBraceForegroundColor(QtGui.QColor("#ffffff"))

        text = bytearray(str.encode("Consolas"))
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, text)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        self.setMinimumSize(0, 200)

    def text(self):
        text = str(super(script_editor_widget, self).text()
                   ).replace('\r\n', '\n')
        return text

    def selectedText(self):
        return str(super(script_editor_widget, self).selectedText())

    def on_margin_clicked(self, nmargin, nline, modifiers):
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)

    def dragEnterEvent(self, event):
        self.setStyleSheet('border : 1px solid white;')
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet('')

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            filepath = str(urls[0].path())[1:]
            if filepath:
                self.drop_signal.emit(filepath)
        self.setStyleSheet('')


class python_lexer(QsciLexerCustom):
    def __init__(self, parent):
        super(python_lexer, self).__init__(parent)

        default_font = QtGui.QFont("Consolas", 9)
        italic_font = QtGui.QFont("Consolas", 9)
        italic_font.setItalic(1)

        self.setDefaultFont(default_font)
        self.setDefaultPaper(QtGui.QColor("#24242b"))
        self.setDefaultColor(QtGui.QColor("#24242b"))

        self.setColor(QtGui.QColor("#ffffff"), 0)   # Style 0: default
        self.setColor(QtGui.QColor("#ff80bb"), 1)   # Style 1: keyword
        self.setColor(QtGui.QColor("gray"), 2)      # Style 2: comment
        self.setColor(QtGui.QColor("#caff80"), 3)   # Style 2: function
        self.setColor(QtGui.QColor("#88c6fc"), 4)   # Style 2: function key
        self.setColor(QtGui.QColor("#e8776f"), 5)   # Style 2: class key
        self.setColor(QtGui.QColor("#88c6fc"), 6)   # Style 2: function call
        self.setColor(QtGui.QColor("#ffe085"), 7)   # Style 2: string
        self.setColor(QtGui.QColor("#e8776f"), 8)   # Style 2: string

        self.setFont(italic_font, 4)
        self.setFont(italic_font, 5)

        self.keyword_list = ["from",
                             "import",
                             "if",
                             "elif",
                             "else",
                             "finally",
                             "try",
                             "except",
                             "for",
                             "while",
                             "return",
                             "in",
                             "as",
                             "=",
                             "+",
                             "*"
                             "-",
                             "/",
                             "*",
                             "!",
                             "<",
                             ">",
                             "@",
                             '__name__',
                             'pass']

        self.function_key_list = ['def', 'class', 'wapi']
        self.class_keys_list = ['self', 'parent']
        self.string_quotes = ['"', "'"]
        self.comment_quotes = ["#"]
        self.boolean_list = ['True', 'False', 'None']
        self.return_list = ['\n', '\r', '\r\n',
                            '\\r', '\\n', '\\r\\n', '\n\n', '\\n\\n']

    def language(self):
        return "Python"

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        elif style == 4:
            return "myStyle_4"
        elif style == 5:
            return "myStyle_5"
        elif style == 6:
            return "myStyle_6"
        elif style == 7:
            return "myStyle_7"
        elif style == 8:
            return "myStyle_8"
        return ""

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        source = ''
        end = editor.length()
        start = 0
        if end > start:
            source = bytearray(end - start)
            editor.SendScintilla(editor.SCI_GETTEXTRANGE, start, end, source)

        if not source:
            return

        index = editor.SendScintilla(editor.SCI_LINEFROMPOSITION, start)
        if index > 0:
            pos = editor.SendScintilla(editor.SCI_GETLINEENDPOSITION, index
                                       - 1)
            state = editor.SendScintilla(editor.SCI_GETSTYLEAT, pos)
        else:
            state = 0

        set_style = self.setStyling
        self.startStyling(start, 0x1f)

        source = source.decode('utf-8')
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        token_list = [(token, len(bytearray(token, "utf-8")))
                      for token in p.findall(source)]

        next_is_fun_name = 0
        string_started = None
        comment_started = None

        for i, token in enumerate(token_list):

            try:
                float(token[0])
                is_number = 1
            except:
                is_number = 0

            if not string_started and not comment_started:

                if token[0] in self.keyword_list:
                    style = 1
                    next_is_fun_name = 0
                elif token[0] in self.function_key_list:
                    style = 4
                    next_is_fun_name = 1
                elif token[0] in self.class_keys_list:
                    style = 5
                    next_is_fun_name = 0
                elif token[0] in self.string_quotes:
                    string_started = token[0]
                    style = 7
                elif token[0] in self.comment_quotes:
                    comment_started = token[0]
                    style = 2
                elif is_number or token[0] in self.boolean_list:
                    style = 8
                    is_number = 0
                else:

                    style = 0

                    if (i+1) < len(token_list):
                        if token_list[i+1][0] == '(':
                            if next_is_fun_name:
                                style = 3
                                next_is_fun_name = 0
                            else:
                                style = 6
                                next_is_fun_name = 0

            elif string_started:
                style = 7
                if token[0] == string_started:
                    string_started = None

            elif comment_started:
                style = 2
                for item in self.return_list:
                    if item in token[0]:
                        comment_started = None
                        break

            self.setStyling(token[1], style)
