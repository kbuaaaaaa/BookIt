import persistent
class Booking(persistent.Persistent):
    def __init__(self,date,time_in,time_out):
        self.date = date
        self.time_in = time_in
        self.time_out = time_out
        self.key = ""
    def getDate(self):
        return str(self.date)
    def getStartTime(self):
        return str(self.time_in)
    def getEndTime(self):
        return str(self.time_out)
    def setDate(self,date):
        self.date = date
    def setTimeIn(self,time):
        self.time_in = time
    def setTimeOut(self,time):
        self.time_out = time
    def get_key(self):
        self.key = f"BookIT{self.date}{self.time_in}{self.time_out}"
        return self.key
    def __str__(self):
        return f"Book at {self.date} In: {self.time_in} Out: {self.time_out}"