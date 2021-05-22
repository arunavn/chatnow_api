from sqlalchemy import Column, Integer, String
from chatnow_api.database import Base
class Users(Base):
    __tablename__= 'users'
    id= Column(Integer, primary_key= True)
    userid= Column(String, unique= True, nullable= False)
    email= Column(String, unique= True, nullable= False)
    password= Column(String, nullable= False)
    name= Column(String, nullable= False)
    about= Column(String, nullable= True)