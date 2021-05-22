from sqlalchemy import or_, and_, select, func
from chatnow_api.db_model.chat_db import Chats, Messages
from chatnow_api.db_model.accounts_db import Users
from difflib import get_close_matches
from datetime import datetime

from chatnow_api.database import db_session
from chatnow_api.utilities.common.utility_classes import Chat, Message
def post_messages(messages, sender= None):
    for m in messages:
        s= m.get('sender', None)
        if s is None:
            m.update({'sender': sender})
            s = sender
        r= m.get('reciever', None)
        if s == r:
            continue
        c= Chats.query.filter(or_( and_(Chats.user1 == r, Chats.user2 == s )  , and_(Chats.user2 == r, Chats.user1 == s) )).first()
        if c is None:
            c= Chats()
            c.id, c.user1, c.user2, c.chatstart= None, s, r, None
            db_session.add(c)
            db_session.commit()
        print(c.__dict__)
        msg= Message(**m)
        msgs= Messages(**msg.__dict__)
        msgs.chatid= c.id
        msgs.status= 'N'
        db_session.add(msgs)
    db_session.commit()

def get_chats(id= None, filterstring= None):
    chats_data= Chats.query.filter(or_( Chats.user1== id , Chats.user2== id )).all()
    other_users= []
    chat_ids= []
    for c in chats_data:
        x, y= c.user1, c.user2
        chat_ids.append(c.id)
        if x != id:
            other_users.append(x)
            c.reciever= x
        else:
            other_users.append(y)
            c.reciever= y
    user_data= Users.query.filter(Users.id.in_(other_users) ).all()
    messages_unread= db_session.query(Messages.chatid, func.count('*')).filter( and_(Messages.chatid.in_(chat_ids), Messages.status== 'N', Messages.sender != id ) ).group_by(Messages.chatid).all()
    #chat_unread_counts = select( [messages_unread.chatid ,func.count(messages_unread.id) ]).select_from(messages_unread)
    latest_messeges_id= db_session.query(Messages.chatid, func.max(Messages.id)).filter( Messages.chatid.in_(chat_ids) ).group_by(Messages.chatid).all()
    message_ids=[]
    for lm in latest_messeges_id:
        message_ids.append(lm[1])
    latest_messages= Messages.query.filter(Messages.id.in_(message_ids)).all()
    chat_dict_list= []
    search_list=[]
    email_list=[]
    for c in chats_data:
        chat_dict= {}
        if int(c.reciever) == int(id):
            continue
        chat_dict.update({'id': c.id})
        chat_dict.update({'reciever': c.reciever})
        r_user= list( filter( lambda u: u.id == c.reciever, user_data  ) )[0]
        chat_dict.update({'otheruserid': r_user.userid})
        search_list.append(r_user.userid)
        chat_dict.update({'othername': r_user.name})
        search_list.append(r_user.name)
        chat_dict.update({'otheremail': r_user.email})
        email_list.append(r_user.email)
        last_msg= list( filter( lambda m: m.chatid == c.id , latest_messages) )[0]
        chat_dict.update({'lastmessage': last_msg.message})
        chat_dict.update({'lastmessageno': last_msg.id})
        chat_dict.update({'lastmessagesentat': last_msg.sentat.timestamp()})
        chat_dict.update({'lastmessagetype': last_msg.messagetype})
        chat_dict.update({'lastmessageby': last_msg.sender})
        chat_dict.update({'lastmessagestatus': last_msg.status})
        #chat_dict.update({'lastmessagetime': last_msg.sentat})
        try:
            u_msg= list( filter( lambda m_u: m_u[0] == c.id  , messages_unread) )[0]
            chat_dict.update({'unread': u_msg[1]})
        except:
            chat_dict.update({'unread': ''})
        #chat_dict.update({'unread': u_msg[1]})
        chat_dict_list.append(chat_dict)

    if filterstring != '' and filterstring != ' ' and filterstring is not None:
        close_matches= get_close_matches(word= filterstring, possibilities= search_list, n= len(chat_dict_list), cutoff= 0.6) 
        chat_dict_list= list( filter( lambda x: (x['othername'] in close_matches or x['otheruserid'] in close_matches  ), chat_dict_list ))
        chat_dict_list = [ dict(t) for t in {  tuple(u.items()) for u in chat_dict_list }  ]
    else:
        chat_dict_list = sorted(  chat_dict_list, key = lambda item: item['lastmessageno'] )
    return chat_dict_list

def read_messages(user= None, queryDict= None):
    if queryDict['otheruser'] == user:
            return []
    c= Chats.query.filter(or_( and_(Chats.user1== user , Chats.user2== queryDict['otheruser']),\
                                 and_(Chats.user2== user , Chats.user1== queryDict['otheruser'])  ) ).all()
    c= c[0]
    mlast= Messages.query.order_by(Messages.id.desc()).limit(1)
    if mlast is not None:
        x= queryDict.get('todt', None)
        if x is None:
            todt= mlast[0].sentat
        else:
            todt = datetime.fromtimestamp(x)
        x= queryDict.get('fromdt', None)
        if x is None:   
            fromdt = datetime.fromtimestamp(0000000000)
        else:
            fromdt = datetime.fromtimestamp(x)
        x= queryDict.get('frommsg', None)
        if x is None:   
            frommsg = 0
        else:
            frommsg = x
        x= queryDict.get('tomsg', None)
        if x is None:   
            tomsg = mlast[0].id
        else:
            tomsg = x
        x= queryDict.get('nprev', None)
        if x is None:   
            nprev = mlast[0].id
        else:
            nprev = x
        
        mlist= Messages.query.filter(
            and_(
                Messages.sentat >= fromdt,
                Messages.sentat <= todt,
                Messages.id >= frommsg,
                Messages.id <= tomsg,
                Messages.chatid == c.id
            )
            ).order_by(Messages.id.desc()).limit(nprev)
        
    else:
        mlist= []

    mlist_unread= []
    msglist= []
    for m in mlist:
        mdict= {}
        mdict.update({'chatid': m.chatid})
        mdict.update({'id': m.id})
        mdict.update({'sender': m.sender})
        rec = user if user != m.sender else queryDict['otheruser']
        mdict.update({'reciever': rec})
        mdict.update({'direction': 'S' if m.sender == user else 'R'})
        if m.status == 'N' and mdict['direction'] == 'R':
            mlist_unread.append(m)
        mdict.update({'message': m.message})
        mdict.update({'messagetype': m.messagetype})
        mdict.update({'status': m.status})
        mdict.update({'sentat': m.sentat.timestamp()})
        msglist.append(mdict)
    msglist= sorted(msglist, key = lambda item: item['id'])
    for mun in mlist_unread:
        mun.status = 'R'
    db_session.commit()
    return msglist

def find_people(current_user, filterstring):
    filtered_users = []
    filtered_user_tmp= []
    filtered_users_email = []
    filtered_users_name = []
    filtered_users_userid = []
    email_list= []
    other_list= []
    filters= '%{}%'.format(filterstring)
    print(filterstring)
    if '@' in filterstring:
        filtered_users_email = Users.query.filter(Users.email.like(filters)).all()
        for fe in filtered_users_email:
            email_list.append(fe.email)
        x =  len(email_list) if len(email_list) > 0 else 1 
        close_matches_email= get_close_matches(word= filterstring, possibilities= email_list, n= x, cutoff= 0.4)
        for cme in close_matches_email:
            user = list(filter( lambda u: u.email == cme, filtered_users_email ))
            if ( len(user) > 0):
                filtered_user_tmp.append(user[0])
    else:
        filtered_users_name = Users.query.filter(Users.name.like(filters)).all()
        for fn in filtered_users_name:
            other_list.append(fn.name)
        filtered_users_userid = Users.query.filter(Users.userid.like(filters)).all()
        for fu in filtered_users_userid:
            other_list.append(fu.userid)
        x =  len(other_list) if len(other_list) > 0 else 1 
        close_matches_other= get_close_matches(word= filterstring, possibilities= other_list, n= x, cutoff= 0.6)
        for cmo in close_matches_other:
            user1 = list(filter( lambda u: u.name == cmo, filtered_users_name ))
            for u1 in user1:
                filtered_user_tmp.append(u1)
            user2 = list(filter( lambda u: u.userid == cmo, filtered_users_userid ))
            if ( len(user2) > 0 ):
                filtered_user_tmp.append(user2[0])
    for u in filtered_user_tmp:
        user_dict = {
            'id' : u.id,
            'userid' : u.userid,
            'name' : u.name,
            'email' : u.email
        }
        if u.id != current_user:
            filtered_users.append(user_dict)
    filtered_users = [ dict(t) for t in {  tuple(u.items()) for u in filtered_users }  ]
    return filtered_users