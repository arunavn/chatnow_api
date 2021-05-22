from sqlalchemy import Column, Integer, String, DateTime
from chatnow_api.database import Base
import datetime
class Chats(Base):
    __tablename__= 'chats'
    id= Column(Integer, primary_key= True)
    user1= Column(Integer, nullable= False)
    user2= Column(Integer, nullable= False)
    chatstart= Column( DateTime, default=datetime.datetime.utcnow, nullable= False)
class Messages(Base):
    __tablename__= 'messages'
    id= Column(Integer, primary_key= True)
    chatid= Column(Integer, nullable= False)
    sender= Column(Integer, nullable= False)
    messagetype= Column(String, nullable= False)
    message= Column(String, nullable= False)
    sentat= Column(DateTime, default=datetime.datetime.utcnow, nullable= False)
    status= Column(String)