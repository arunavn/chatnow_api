from marshmallow import Schema, fields, validate
from webargs import fields, validate
class MessagePost(Schema):
    sender= fields.Integer()
    reciever= fields.Integer(required=True)
    messagetype= fields.String(required=True)
    message= fields.String(required=True)


def message_get_parser():
    message_args = {
        'otheruser': fields.Integer(required= True),
        'fromdt': fields.Str(),
        'todt': fields.Str(),
        'frommsg': fields.Integer(),
        'tomsg': fields.Integer(),
        'nprev': fields.Integer()
    }
    return message_args





