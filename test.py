import sys
import calendar
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5 import QtGui

class AppDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)

        menuMonths = self.menuBar().addMenu('Months')
        menuMonths.triggered.connect(self.printValue)

        for i in range(1, 13):
            action = menuMonths.addAction(QtGui.QIcon('C:/Users/Leo/Desktop/sorcieres/2.jpg'), calendar.month_name[i])
            action.setCheckable(True)

    def printValue(self, action):
        print('{0}-{1}'.format(action.text(), action.isChecked()))

app = QApplication(sys.argv)        

demo = AppDemo()
demo.show()

sys.exit(app.exec_())