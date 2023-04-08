import Board
import uuid
import hashlib

class User:
    username_list = []
    email_list = []
    fullname = []
    passwd = []
    session_dict = {}
    salt = '456'
    def __init__(self, username, email, fullname, passwd):
        if username in User.username_list:
            raise UserExistsException('Username exists')
        if email in User.email_list:
            raise UserExistsException('Email exists')
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = hashlib.sha256((passwd + User.salt).encode()).hexdigest()
        print(self.passwd)
        #TODO register user
        User.username_list.append(username)
        User.email_list.append(email)
        User.fullname.append(fullname)
        User.passwd.append(passwd)

    def __str__(self):
        return str({
            "username": self.username,
            "email": self.email,
            "fullname": self.fullname,
            "passwd": self.passwd,
        })
    def get(self):
        return self.__str__()
    def update_helper(self, username=None, email=None, fullname=None, passwd=None):
        if username!=None:
            if username in User.username_list:
                raise UserExistsException('Username exists')
            self.username = username
        if email!=None:
            if email in User.email_list:
                raise UserExistsException('Email exists')
            self.email = email
        if fullname != None:
            self.fullname = fullname
        if username != None:
            self.passwd = passwd

    def update(self, username=None, email=None, fullname=None, passwd=None):
        try:
            self.update_helper(username, email, fullname, passwd)
        except UserExistsException as e:
            print(f'Error: {e}')

    def delete(self):
        pass    #TODO

    def auth(self,plainpass):
        if self.passwd == hashlib.sha256((plainpass + User.salt).encode()).hexdigest():
            print("Matched")
            return True
        else:
            print("Not matched")
            return False

    def login(self):
        random_token = str(uuid.uuid4())
        User.session_dict[self.username] = random_token
        return random_token

    def checksession(token):
        for value in User.session_dict.values():
            if value == token:
                print("Valid")
                return True
        print("Invalid")
        return False

    def logout(self):
        del User.session_dict[self.username]

    def callback(self,message):
        print(message)
    def turncb(self,message):
        print(message)
        return input()

class UserExistsException(BaseException):
    pass



