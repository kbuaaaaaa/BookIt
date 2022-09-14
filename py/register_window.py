from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import ZODB, ZODB.FileStorage, persistent, BTrees.OOBTree, transaction
import sys
import Ui_Register
from user import User
from os import environ
# environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"
class Register(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Register.Ui_Form()
        self.ui.setupUi(self)

        self.ui.registerBtn.clicked.connect(lambda:self.register())

    def register(self):
        if self.ui.lineEdit_password.text() != self.ui.lineEdit_confirm_password.text():
            msg = QMessageBox()
            msg.setText("Password mismatch!")
            msg.setWindowTitle("Warning!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        email = self.ui.lineEdit_email.text()
        first_name = self.ui.lineEdit_firstname.text()
        last_name = self.ui.lineEdit_lastname.text()
        password = self.ui.lineEdit_password.text()
        user = User(email,first_name,last_name,password)
        if email == "" or first_name == "" or last_name == "" or password == "":
            msg = QMessageBox()
            msg.setText("You have enter empty field")
            msg.setWindowTitle("Warning!")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return
        #connect and link to ZODB database
        storage = ZODB.FileStorage.FileStorage('userDB.fs')
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root()
        root[email] = user
        transaction.commit()
        connection.close()
        db.close()

        ##Create List for booking
        storage = ZODB.FileStorage.FileStorage('bookingsDB.fs')
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root()
        root[email] = []
        transaction.commit()
        connection.close()
        db.close()
        ##
        print("register complete") ##do something such as transition into login ui
        msg = QMessageBox()
        msg.setText("Register Complete!")
        msg.setWindowTitle("Register")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    suppress_qt_warnings()

    # create and show mainWindow
    mainWindow = Register()
    mainWindow.show()

    sys.exit(app.exec_())
