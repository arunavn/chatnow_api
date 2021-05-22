import string
from celery import Celery
from random import shuffle, choice
from flask import current_app
from flask_mail import Message, Mail
from chatnow_api.utilities.common.utility_classes import MailData


def generate_password():
    password = []
    for i in range(3):
        alpha_u = choice(string.ascii_uppercase)
        symbol = choice("@#$%&*")
        alpha_l = choice(string.ascii_lowercase)
        numbers = choice(string.digits)
        password.append(alpha_u)
        password.append(alpha_l)
        password.append(symbol)
        password.append(numbers)
    shuffle(password)
    passwords = "".join(str(x)for x in password)
    return passwords


def send_mail(mailData= None):
    msg= Message(  recipients= [mailData.sentTo],
                    sender= mailData.sentFrom,
                    body=mailData.body,
                    subject=mailData.subject)

    with current_app.app_context():
        mail= Mail()
        mail.send(msg)

def send_password(user= None):
    if user is not None:
        maildata= {
            'sentFrom' : (current_app.config.get('MAIL_USERNAME', None), 'Password Reset'),#current_app.config.get('MAIL_USERNAME', None) ,
            'sentTo' : "an.appstest@gmail.com",
            'body' : '',
            'subject': 'Chatnow Password'
        }
        maildata['body'] = """
        Dear {},
        \tplease use this password to login->
        \tuser id. - {},
        \tpassword - {},
        Thanks,
        Chatnow.
        """.format(user.name, user.userid, user.password)
        mailData= MailData(**maildata)
        send_mail(mailData)
def send_userid(user= None):
    if user is not None:
        maildata= {
            'sentFrom' : (current_app.config.get('MAIL_USERNAME', None), 'userid'),#current_app.config.get('MAIL_USERNAME', None) ,
            'sentTo' : "an.appstest@gmail.com",
            'body' : '',
            'subject': 'Chatnow userid'
        }
        maildata['body'] = """
        Dear {},
        \tplease use this userid to login->
        \tuser id. - {},
        Thanks,
        Chatnow.
        """.format(user.name, user.userid)
        mailData= MailData(**maildata)
        send_mail(mailData)


    
        