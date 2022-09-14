from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys

import Ui_Mainwindow
import read_qr_window
from read_qr_window import ReadQR
from manage_window import Manage_Window

class Menu(QMainWindow):
    def  __init__(self,user,login_win):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.__login_win = login_win
        self.Stack = QStackedWidget()
        self.stack1 = self
        if user == 'admin':
            self.unlock_ui = Ui_unlock.Ui_Dialog()
            self.Dialog = QtWidgets.QDialog()
            self.unlock_ui.setupUi(self.Dialog)
            self.stack2 = self.Dialog
            self.stack3 = Admin_Manage_Window(self.Stack)
        else:
            self.stack2 = ReadQR(user,self.Stack)
            self.stack3 = Manage_Window(user,self.Stack)

        self.Stack.addWidget(self.stack1)
        self.Stack.addWidget(self.stack2)
        self.Stack.addWidget(self.stack3)
        self.Stack.setFixedHeight(500)
        self.Stack.setFixedWidth(400)
        self.Stack.show()

        self.ui.unlock_btn.clicked.connect(self.open_unlock)
        self.ui.mange_btn.clicked.connect(self.open_manage)
        self.ui.logout_btn.clicked.connect(self.log_out)

    def open_unlock(self):
        self.Stack.setCurrentIndex(1)

    def open_manage(self):
        
        self.Stack.setCurrentIndex(2)
        
    def log_out(self):
        self.close()
        self.Stack.close()
        self.__login_win.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = Menu("admin")
    mainWindow.show()

    sys.exit(app.exec_())
