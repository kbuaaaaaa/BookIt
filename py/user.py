import ZODB, ZODB.FileStorage, persistent, BTrees.OOBTree, transaction

class User(persistent.Persistent):
    def __init__(self,email,first_name,last_name,password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
    def get_name(self):
        return str(self.first_name+" "+self.last_name)
    def get_email(self):
        return self.email
    def get_password(self):
        return self.password

    def __str__(self):
        return  f"User = {self.email} Password = {self.password} Name = {self.first_name} {self.last_name}"

