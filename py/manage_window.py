from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from booking import Booking
# from Bookings import Booking
import Ui_Qrcode
import Ui_Show_Qr
import ZODB, ZODB.FileStorage, ZODB.DB, persistent, BTrees.OOBTree, transaction
import Ui_Manage2
import sys
import pyqrcode


class Manage_Window(QWidget):
    # class constructor
    def __init__(self,user,stack_widget):
        # call QWidget constructor
        super().__init__()
        self.__currentUser = user
        self.__stack = stack_widget
        self.ui = Ui_Manage2.Ui_Form()
        self.ui.setupUi(self)
        self.ui.frame.hide()
        self.displayBookings()
        self.ui.delete_btn.setEnabled(False)
        self.ui.change_btn.setEnabled(False)
 
        self.ui.add_btn.clicked.connect(self.add)
        self.ui.change_btn.clicked.connect(self.change)
        self.ui.delete_btn.clicked.connect(self.delete)
        self.ui.book_btn.clicked.connect(self.book)
        self.ui.back_btn.clicked.connect(self.back)
        self.ui.tableWidget.selectionModel().selectionChanged.connect(self.on_selectionChanged)
 
     

    def displayBookings(self):
        try:
            storage = ZODB.FileStorage.FileStorage('bookingsDB.fs')
            db = ZODB.DB(storage)
            connection = db.open()
            root = connection.root()
            for booking in root[self.__currentUser]:
                # print(booking)
                self.ui.tableWidget.insertRow ( self.ui.tableWidget.rowCount() )
                self.ui.tableWidget.setItem( self.ui.tableWidget.rowCount()-1, 0, QTableWidgetItem(str(booking.getDate())))
                self.ui.tableWidget.setItem( self.ui.tableWidget.rowCount()-1, 1, QTableWidgetItem(str(booking.getStartTime())))
                self.ui.tableWidget.setItem( self.ui.tableWidget.rowCount()-1, 2, QTableWidgetItem(str(booking.getEndTime())))

            connection.close()
            db.close()
        except:
            print("Cannot access to Database")

    def reset_value(self):
        self.ui.book_btn.setText('Book')
        self.ui.dateTimeEdit_in.clear()
        self.ui.dateTimeEdit_out.clear()
        while self.ui.tableWidget.rowCount()!=0:
            self.ui.tableWidget.removeRow(0)
        self.ui.tableWidget.clear()

    def add(self):
        self.ui.frame.show()


    def change(self):
        #Set Qtime edit equal to that select row
        self.set_selected_time_edit()
        self.ui.book_btn.setText('Change')
        self.ui.frame.show()
            
    def delete(self):
        self.set_selected_time_edit()
        self.ui.book_btn.setText('Delete')
        self.ui.frame.show()

    def book(self):
       
        flag = False
        try:
            storage = ZODB.FileStorage.FileStorage('bookingsDB.fs')
            db = ZODB.DB(storage)
            connection = db.open()
            root = connection.root()
            bookingList = root[self.__currentUser]
        except:
            print("Cant acess database")
            exit()
            
        if self.ui.book_btn.text()=='Book':
            time_in = self.ui.dateTimeEdit_in.dateTime()
            time_in = time_in.toString('M/d/yyyy hh:mm ').split()

            time_out = self.ui.dateTimeEdit_out.dateTime()
            time_out = time_out.toString('M/d/yyyy hh:mm ').split()

            #Validate the date time in and out with the previous booking too
            new_booking = Booking(time_in[0],time_in[1],time_out[1])
            if not self.isTimeOverLap(new_booking,root):
                key = new_booking.get_key()
                self.gen_QR(key)
                flag = True
                bookingList.append(new_booking)
            else:
                print("Your time overlap with other")
                msg = QMessageBox()
                msg.setWindowTitle('Error')
                msg.setText('You time overlap with other!\nPlease select other time')
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                transaction.commit()
                connection.close()
                db.close()
                return

        elif self.ui.book_btn.text() == 'Change':
            select_row = self.ui.tableWidget.currentRow()
            time_in = self.ui.dateTimeEdit_in.dateTime()
            time_in = time_in.toString('M/d/yyyy hh:mm ').split()

            time_out = self.ui.dateTimeEdit_out.dateTime()
            time_out = time_out.toString('M/d/yyyy hh:mm ').split()

            #Validate the datem time in and out with the data base
            select_booking = bookingList[select_row]
            select_booking.setDate(time_in[0])
            select_booking.setTimeIn(time_in[1])
            select_booking.setTimeOut(time_out[1])
            if not self.isTimeOverLap(select_booking,root):
                key = select_booking.get_key()
                self.gen_QR(key)
                flag = True
                bookingList[select_row] = select_booking
            else:
                print("Your time overlap with other")
                msg = QMessageBox()
                msg.setWindowTitle('Error')
                msg.setText('You time overlap with other!\nPlease select other time')
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()
                return
        elif self.ui.book_btn.text() == 'Delete':
            select_row = self.ui.tableWidget.currentRow()
            bookingList.pop(select_row)
            
        root[self.__currentUser] = bookingList
        transaction.commit()
        connection.close()
        db.close()

        self.Form = QtWidgets.QWidget()
        ui = Ui_Show_Qr.Ui_Dialog(flag)
        ui.setupUi(self.Form)
        self.Form.show()
        self.reset_value()
        self.displayBookings()
        self.ui.frame.hide()
        self.__stack.setCurrentIndex(0)
    def on_selectionChanged(self,selected,dselected):
        print(selected)
        self.ui.delete_btn.setEnabled(True)
        self.ui.change_btn.setEnabled(True)       

    def set_selected_time_edit(self):
        select_row = self.ui.tableWidget.selectedItems()
        date = select_row[0].text()
        time_in = select_row[1].text()
        time_out = select_row[1].text()
        day,month,year = [int(x) for x in date.split('/')]
        h1,m1 = [int(x) for x in time_in.split(':')]
        h2,m2 = [int(x) for x in time_out.split(':')]
        d = QDate(year,month,day)
        t1 = QDateTime(d,QTime(h1,m1))
        t2 = QDateTime(d,QTime(h2,m2))
        self.ui.dateTimeEdit_in.setDateTime(t1)
        self.ui.dateTimeEdit_out.setDateTime(t2)

    def gen_QR(self,key):
        print(key)
        qr_code = pyqrcode.create(key)
        qr_code.png('QR_CODE.PNG')
        return

    def isTimeOverLap(self,book,root):
        date = book.getDate()
        start = book.getStartTime()
        end = book.getEndTime()
        day,month,year = [int(x) for x in date.split('/')]
        hour_in,min_in = [int(x) for x in start.split(':')]
        hour_out,min_out = [int(x) for x in end.split(':')]
        d = QDate(year,month,day)

        time_in =QDateTime(d,QTime(hour_in,min_in))
        time_out = QDateTime(d,QTime(hour_out,min_out))

        booking_log = []
        for user,bookingList in root.items():
            for booking in bookingList:
                booking_log.append(booking)
                print(booking)

        if len(booking_log) != 0:
            for b in booking_log:
                temp_date = b.getDate()
                temp_day,temp_month,temp_year = [int(x) for x in temp_date.split('/')]
                temp_d = QDate(temp_year,temp_month,temp_day)
                if temp_d == d:
                    print("Same date")
                    temp_start = b.getStartTime()
                    temp_end = b.getEndTime()

                    temp_hour_in,temp_min_in = [int(x) for x in temp_start.split(':')]
                    temp_hour_out,temp_min_out = [int(x) for x in temp_end.split(':')]

                    temp_date = QDate(temp_year,temp_month,temp_day)
                    temp_time_in =QDateTime(temp_date,QTime(temp_hour_in,temp_min_in))
                    temp_time_out = QDateTime(temp_date,QTime(temp_hour_out,temp_min_out))
                    print(temp_time_in,temp_time_out,time_in,time_out)
                    if temp_time_in<time_in<temp_time_out or temp_time_in<time_out<temp_time_out:
                        return True
                else:
                    continue

        return False

    def back(self):
        self.reset_value()
        self.__stack.setCurrentIndex(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mainWindow = Manage_Window("User")
    mainWindow.show()

    sys.exit(app.exec_())
