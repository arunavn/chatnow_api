
from chatnow_api.utilities.common.utility_classes import ReturnStructure, User
from werkzeug.security import safe_str_cmp
from sqlalchemy import or_
from flask_jwt_extended import create_access_token
from chatnow_api.db_model.accounts_db import Users
from chatnow_api.database import db_session
from chatnow_api.utilities.common.utility_functions import generate_password, send_password, send_userid

user1 =     { 'id': '1',
            'userid': 'bob12',
            'email': 'bob12@gmail.com',
            'name': 'bob samuels',
            'password': 'asd',
            'about': 'Always high' }
        

users= []
users.append(User(**user1))

userid_table = {u.userid: u for u in users}
id_table = {u.id: u for u in users}


def get_users(_id= None, userid= None, email= None):
    filtered_users= []
    ret_data= ReturnStructure()
    #begin replace with query
    if (_id != None or email != None or userid != None):
        filtered_users = Users.query.filter(or_(Users.id == _id, Users.userid == userid, Users.email == email  )).all()
    else:
        filtered_users = Users.query.all()
    #for uo in users:
    #    u= uo.__dict__
    #    if (u['userid'] == userid or userid is None)\
    #        and (u['email'] == email or email is None)\
    #        and (u['id'] == _id or _id is None):
    #        uo1= User(**u)
    #        filtered_users.append(uo1)
    #End replace with query
    filtered_users_out=[]
    for uo in filtered_users:
        u= uo.__dict__
        u['password'] = '*'
        u_out= User(**u)
        filtered_users_out.append(u_out)
    if len(filtered_users_out)==0:
        ret_data.set_structure('E', 'Could not find any user with given filter ', None)
    else:
        ret_data.set_structure('S', 'Returning fetched user', filtered_users_out)
    return ret_data

def get_user(findby, value, hidePersonal= True, hidePassword= True, func= None):
    user= None
    show_fields= []
    if findby is None:
        findby= 'userid'
    ret_data= ReturnStructure()
    #begin replace with query
    uo, user= None, None
    if findby == 'id':
        uo = Users.query.filter(Users.id == value).first()
    elif findby == 'userid':
        uo = Users.query.filter(Users.userid == value).first()
    elif findby == 'email':
        uo= Users.query.filter(Users.email == value).first()
    #for uo in users:
    #    u= uo.__dict__
    #    if u[findby] == value:
    #        user= User(**uo.__dict__)
    #End replace with query
    if uo is not None:
        x= uo.userid
        user= User(**uo.__dict__)
    if user is None:
        ret_data.set_structure('E', 'Could not find user with given {}'.format(findby), 'filter')
    else:
        if func not in [None, 'forgotuserid']:
            if hidePassword:
                user.password= '*'
            if hidePersonal:
                user= User( **{'id': user.id, 'userid': user.userid } )
        elif func == 'forgotuserid':
            user= User( **{'id': user.id, 'userid': user.userid, 'name': user.name } )
            send_userid(user)
        ret_data.set_structure('S', 'Returning fetched user', user)
    return ret_data

def get_user_by_uid(userid):
    user= None
    ret_data= ReturnStructure()
    #begin replace with query
    for uo in users:
        u= uo.__dict__
        if u['userid'] == userid:
            u['password'] = '*******'
            user= uo
    #End replace with query
    if user is None:
        ret_data.set_structure('E', 'Could not find user with given user id', None)
    else:
        ret_data.set_structure('S', 'Returning fetched user', user)
    return ret_data
def get_user_by_id(_id):
    user= None
    ret_data= ReturnStructure()
    #begin replace with query
    for uo in users:
        u= uo.__dict__
        if u['id'] == _id:
            user= uo
    #End replace with query
    if user is None:
        ret_data.set_structure('E', 'Could not find user with given id', None)
    else:
        ret_data.set_structure('S', 'Returning fetched user', user)
    return ret_data
def get_user_by_eid(email):
    user= None
    ret_data= ReturnStructure()
    #begin replace with query
    for uo in users:
        u= uo.__dict__
        if u['email'] == email:
            u['password'] = '*******'
            user= uo
    #End replace with query
    if user is None:
        ret_data.set_structure('E', 'Could not find user with given email id', None)
    else:
        ret_data.set_structure('S', 'Returning fetched user', user)
    return ret_data
def post_user(userdata):
    eid = get_user('email', userdata['email'], hidePersonal=False)
    uid = get_user('userid', userdata['userid'], hidePersonal= False)
    ret_data= ReturnStructure()
    ret_data.set_structure('S', 'Inserted user', None)
    if uid.pStatus != 'E':
        ret_data.set_structure('E', 'userid already registered', None)
        return ret_data
    elif eid.pStatus != 'E':
        ret_data.set_structure('E', 'email already registered', None)
        return ret_data
    #begin replace with query
    user= Users(**userdata)
    user.password = generate_password()
    user.id= None
    db_session.add(user)
    db_session.commit()
    #user= Users(**userdata)
    #users.append(user)
    #begin replace with query
    x= user.userid
    u = get_user('userid', x, hidePersonal= False)
    if u.pStatus != 'E':
        ret_data.set_structure('S', 'Inserted user', User(**u.data.__dict__))
        #task= send_password.delay(user)
        send_password(user)
    else:
        ret_data.set_structure('E', 'Could not register user', None)
    return ret_data
def patch_user(findby, value, userdata, func= None):
    dontTouch= ['id']
    ret_user= get_user(findby, value, hidePersonal=False, hidePassword= True)
    if ret_user.pStatus != 'E':
        uo = Users.query.filter(Users.id == ret_user.data.id).first()
        if func in ['update', None]:
            userdata = {key:value for key, value in userdata.items() if value is not None and key not in dontTouch}
            (ret_user.data.__dict__).update(userdata)
            #begin replace with query
            if uo is not None:
                for key, value in userdata.items:
                    setattr(uo, key, value)
                db_session.commit()
                #for i, u in enumerate(users):
                #    if u.id == ret_user.data.id:
                #        users[i]= ret_user.data
                ret_user.pMessage = 'Updated user'
        elif func == 'forgotpassword':
            ret_user.pStatus = 'S'
            ret_user.pMessage = 'password reset succesfull'
            uo.password = generate_password()
            db_session.commit()
            x= uo.userid
            send_password(User(**uo.__dict__))
        elif func=='changepass':
            if uo.password != userdata.get('password', None) :
                ret_user.pStatus = 'E'
                ret_user.pMessage = 'Invalid old password'
                return ret_user
            elif userdata.get('newpassword', None) != userdata.get('cnfpassword', None):
                ret_user.pStatus = 'E'
                ret_user.pMessage = 'passwords do not match'
                return ret_user
            else:
                if userdata.get('newpassword', None) is not None:
                    uo.password = userdata.get('newpassword', None)
                    db_session.commit()

        elif func == 'changeemail':
            new_email= userdata.get('email')
            if new_email is None:
                ret_user.pStatus = 'E'
                ret_user.pMessage = 'Please provide email'
                return ret_user

            if ( safe_str_cmp(uo.password, userdata.get('password', None))
                and userdata.get('password', None) is not None ):
                uo.password = generate_password()
                uo.email = new_email
                db_session.commit()
                x= uo.userid
                ret_user.pStatus = 'S'
                ret_user.pMessage = 'email change successfull'
                send_password(User(**uo.__dict__))
            else:
                ret_user.pStatus = 'E'
                ret_user.pMessage = 'Invalid old password'
        #end replace with query
    return ret_user

def delete_user(findby, value):
    global users
    ret_user= get_user(findby, value)
    if ret_user.pStatus != 'E':
        #begin replace with query
        users = [ u for u in users if u.id != (ret_user.data).id]
        ret_user.pMessage = 'Deleted user'
        #begin replace with query
    return ret_user
