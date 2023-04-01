



class User:
    def __init__(self, username, email, fullname, passwd):
        if self.check_exists(username, email):
            raise UserExistsException()
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd
        #TODO register user
    def __str__(self):
        return str({
            "username": self.username,
            "email": self.email,
            "fullname": self.fullname,
            "passwd": self.passwd,
        })
    def get(self):
        return self.__str__()
    def update(self, username=None, email=None, fullname=None, passwd=None):
        if username!=None:
            if self.check_exists(username, None):
                raise UserExistsException()
            self.username = username
        if email!=None:
            if self.check_exists(None, email):
                raise UserExistsException()
            self.email = email
        if fullname != None:
            self.fullname = fullname
        if username != None:
            self.passwd = passwd
    def delete(self):
        pass    #TODO
    def check_exists(self,username,email):
        return False    #TODO
    def auth(self,plainpass):
        pass    #TODO
    def login(self):
        pass #TODO
    def checksession(token):
        pass #TODO
    def logout(self):
        pass #TODO

class UserExistsException():
    pass



