import ZODB, ZODB.FileStorage, persistent, BTrees.OOBTree, transaction
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from os import environ
from register_window import Register
from mainwindow import Menu
import Ui_Login
import sys
import user
# environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"

class Login(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Login.Ui_Form()
        self.ui.setupUi(self)

        self.ui.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.ui.login_btn.clicked.connect(self.login)
        self.ui.label_register.clicked.connect(self.open_register)

    def login(self):
        email = self.ui.lineEdit_email.text()
        password = self.ui.lineEdit_password.text()

        storage = ZODB.FileStorage.FileStorage('userDB.fs')
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root()
        for k,v in root.items():
            if k == email:
                if password == v.get_password():
                    print("login success")
                    connection.close()
                    db.close()
                    self.mainwindow = Menu(email,self)
                    self.mainwindow.show()
                    self.clear_text_entry()
                    self.hide()
                    #transition to login page
                    return
                else:
                    continue
        msg = QMessageBox()
        msg.setText("Incorrect username or password")
        msg.setWindowTitle("Incorrect!")
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()
        connection.close()
        db.close()
        self.clear_text_entry()
    def open_register(self):
        self.register_win = Register()
        self.register_win.show()

    def clear_text_entry(self):
        self.ui.lineEdit_email.clear()
        self.ui.lineEdit_password.clear()
if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = Login()
    mainWindow.show()

    sys.exit(app.exec_())
