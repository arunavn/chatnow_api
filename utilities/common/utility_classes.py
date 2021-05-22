class ReturnStructure:
    def __init__(self, pStatus='', pMessage= '', data= None):
        self.pStatus= pStatus
        self.pMessage= pMessage
        self.data= data
    def set_structure(self, pStatus, pMessage, data= None ):
        self.pStatus= pStatus
        self.pMessage= pMessage
        self.data= data

class User:
    def __init__(self, **entries):
        self.id= entries.get('id', None)
        self.userid= entries.get('userid', None)
        self.email= entries.get('email', None)
        self.password= entries.get('password', None)
        self.name= entries.get('name', None)
        self.about= entries.get('about', None)
    def set_user(self, **entries):
        entries = { key: value for key, value in entries.items if value is not None }
        self.__dict__.update(entries)

class Chat:
    def __init__(self, **entries):
        self.id= entries.get('id', None)
        self.user1= entries.get('user1', None)
        self.user2= entries.get('user2', None)
        self.chatstart= entries.get('chatstart', None)
    def set_chat(self, **entries):
        entries = { key: value for key, value in entries.items if value is not None }
        self.__dict__.update(entries)

class Message:
    def __init__(self, **entries):
        self.id= entries.get('id', None)
        self.sender= entries.get('sender', None)
        self.messagetype= entries.get('messagetype', None)
        self.message= entries.get('message', None)
        self.status= entries.get('status', None)
    def set_message(self, **entries):
        entries = { key: value for key, value in entries.items if value is not None }
        self.__dict__.update(entries)


class MailData:
    def __init__(self, **mailData):
        self.sentTo= mailData.get('sentTo', None)
        self.sentFrom= mailData.get('sentFrom', None)
        self.subject= mailData.get('subject', None)
        self.body= mailData.get('body', None)