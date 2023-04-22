import uuid
import hashlib
from threading import Lock

class User:
    Command_list= None
    username_list = []
    email_list = []
    fullname = []
    passwd = []
    session_dict = {}
    salt = '456'

    # def __init__(self, username, email, fullname, passwd):
    def __init__(self, client_socket, address):
        """
        Initializes a new user object.
        Checks if the provided username and email are unique, and if not, raises a UserExistsException.
        Stores the hashed password (created by combining the provided password with the salt) in the user object.
        """
        #super().__init__(self)

        self.mutex=Lock()
        self.mutex.acquire()

        self.address=address
        self.client_socket=client_socket
        #self.monopoly=monopoly

        # get username from client
        self.client_socket.send("enter your username, email, fullname, passwd in this order with space between them\n".encode('utf-8'))
        username, email, fullname, passwd = self.client_socket.recv(1024).decode('utf-8').split()

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
    '''def run(self):
        print(f"User {self.username} connected from {self.address[0]}:{self.address[1]}")

        # attaching user
        monopoly.attach(self, self.callback, self.turncb)

        # wait for user to respond with ready
        self.client_socket.send("write \"ready\" when you are".encode('utf-8'))
        ready_msg = self.client_socket.recv(1024).decode('utf-8').strip()
        while ready_msg != "ready":
            self.client_socket.send(f"Invalid message {ready_msg}. say \"ready\" when you are ready".encode('utf-8'))
            ready_msg = self.client_socket.recv(1024).decode('utf-8').strip()
        monopoly.ready(self)

        # barrier waiting it will be opened by the last user in board
        if monopoly.WaitingState == True:
            self.mutex.acquire()

        # waiting for our turns
        # callback is done in monopoly here we only do turncb
        while True:  # TODO change this to end when user detaches
            with self.mutex:
                # TODO'''
    def __str__(self):
        """
        Returns a string representation of the user object,
        which includes the username, email, fullname, and hashed password in a dictionary format.
        """
        return str({
            "username": self.username
        })
    def get(self):
        """
        Calls the __str__() method and returns its result,
        which is the string representation of the user object.
        """
        return self.__str__()
    def update_helper(self, username=None, email=None, fullname=None, passwd=None):
        """
        A helper function to update user information.
        Updates the user's username, email, fullname, and password based on the provided arguments.
        If a new username or email already exists in the respective lists, raises a UserExistsException.
        """
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
        """
        Calls the update_helper() function to update the user's information.
        If a UserExistsException is raised, catches it and prints an error message.
        """
        try:
            self.update_helper(username, email, fullname, passwd)
        except UserExistsException as e:
            print(f'Error: {e}')

    def delete(self):
        """
        A placeholder method for deleting a user
        """
        pass    #TODO

    def auth(self, plainpass):
        """
        Compares the hash of the provided plain password (combined with the salt) with the stored hashed password.
        If they match, returns True and prints "Matched", otherwise returns False and prints "Not matched".
        """
        if self.passwd == hashlib.sha256((plainpass + User.salt).encode()).hexdigest():
            print("Matched")
            return True
        else:
            print("Not matched")
            return False

    def login(self):
        """
        Generates a random session token for the user using the uuid library and
        stores it in the dict with the user's username as the key.
        """
        random_token = str(uuid.uuid4())
        User.session_dict[self.username] = random_token
        return random_token

    def checksession(token):
        """
        Checks if the provided session token is valid
        """
        for value in User.session_dict.values():
            if value == token:
                print("Valid")
                return True
        print("Invalid")
        return False

    def logout(self):
        """
        Removes the user's session token from the session
        """
        del User.session_dict[self.username]

    def callback(self, message):
        """
        Prints the provided message.
        """
        self.client_socket.send((message+"\n").encode('utf-8'))

    def turncb(self, message):
        """
        Prints the provided message and returns the user input obtained using the input() function.
        """
        self.client_socket.send((message+"\n").encode('utf-8'))
        return self.client_socket.recv(1024).decode('utf-8').strip()


    # Below 2 functions are only for testing phase 1 rolls and actions are predetermined for deneme_in
    def setCommandList(self,rl):
        self.Command_list=rl
    def turncb2(self, message):
        """
        Prints the provided message and returns the user input obtained using the input() function.
        """
        print(message)
        if self.Command_list:
            return self.Command_list.pop(0)
        else:
            return input()

class UserExistsException(BaseException):
    pass

