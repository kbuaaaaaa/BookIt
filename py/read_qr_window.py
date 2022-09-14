from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from booking import Booking#temp
import Ui_Qrcode
import Ui_unlock
import ZODB, ZODB.FileStorage, ZODB.DB, persistent, BTrees.OOBTree, transaction
import cv2
import sys

class ReadQR(QWidget):
    # class constructor
    def __init__(self,user,stack_widget):
        # call QWidget constructor
        super().__init__()
        self.ui = Ui_Qrcode.Ui_Form()
        self.ui.setupUi(self)
        self.__currentUser = user
        self.__stack = stack_widget
        # create a timer
        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        # set control_bt callback clicked  function
        self.ui.scan_btn.clicked.connect(self.controlTimer)
        self.ui.cancel_btn.clicked.connect(self.stopTimer)

    # view camera
    def viewCam(self):
        # read image in BGR format
        ret, image = self.cap.read()
        #decode the qrcode
        data, bbox, _ = self.detector.detectAndDecode(image)
        #check if there is a QRCode in the image   
        if data:
            print("QR decode:",data)
            storage = ZODB.FileStorage.FileStorage('bookingsDB.fs')
            try:
                db = ZODB.DB(storage)
                connection = db.open()
                root = connection.root()
                bookingList = root[self.__currentUser]
                for book in bookingList:
                    print(book.get_key())
                    print(data==book.get_key())
                    if str(data.strip()) == str(book.get_key().strip()) and self.time_validation(book):
                        print("login success!")
                        
                        self.stopTimer()
                        self.unlock_ui = Ui_unlock.Ui_Dialog()
                        self.Dialog = QtWidgets.QDialog()
                        self.unlock_ui.setupUi(self.Dialog)
                        self.Dialog.show()
                        
                        #open login success unlock door
            except:
                print("Error")
            finally:
                transaction.commit()
                connection.close()
                db.close()
            ##continue do something after decode QR

        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))
        
    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # create QRCode detector
            self.detector = cv2.QRCodeDetector()
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.ui.scan_btn.setText("Stop")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.ui.image_label.clear()
            self.ui.scan_btn.setText("Start")

    def stopTimer(self):
        try:
            self.cap.release()
        except:
            print("Not even start camera")
        self.timer.stop()
        self.ui.image_label.clear()
        self.__stack.setCurrentIndex(0)

    def time_validation(self,book):
        now = QDateTime.currentDateTime()
        date = book.getDate()
        time_in = book.getStartTime()
        time_out = book.getEndTime()

        day,month,year = [int(x) for x in date.split('/')]
        h1,m1 = [int(x) for x in time_in.split(':')]
        h2,m2 = [int(x) for x in time_out.split(':')]
        d = QDate(year,month,day)
        t_in = QDateTime(d,QTime(h1,m1))
        t_out= QDateTime(d,QTime(h2,m2))

        if t_in<now<t_out:
            return True
        else:
            return False

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create and show mainWindow
    mainWindow = ReadQR("User")
    mainWindow.show()

    sys.exit(app.exec_())
