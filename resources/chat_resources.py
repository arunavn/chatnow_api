from flask_restful import Resource
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_kwargs
from webargs import fields
from chatnow_api.utilities.chat import chat_parsers, chat_utility
from marshmallow import ValidationError

class Chats(Resource):
    @use_kwargs({'filterstring': fields.Str()}, location= 'query')
    @jwt_required()
    def get(self, **kwargs):
        current_identity= get_jwt_identity()
        filterstring= kwargs.get('filterstring', None)
        return chat_utility.get_chats(filterstring= filterstring, id= current_identity), 200
        
class People(Resource):
    @use_kwargs({'filterstring': fields.Str(required= True)}, location= 'query')
    @jwt_required(optional= True)
    def get(self, **kwargs):
        current_identity= get_jwt_identity()
        filterstring= kwargs.get('filterstring', None)
        return chat_utility.find_people(current_identity, filterstring), 200



class Chat(Resource):
    def get(self):
        return { 'msg:':'Incorrect password'}, 405
class Messages(Resource):
    #@use_args(chat_parsers.MessagePost(many= True))
    @jwt_required()
    def post(self):
        try:
            messages= chat_parsers.MessagePost( many=True).load(request.get_json())
            chat_utility.post_messages(messages= messages, sender= get_jwt_identity())
            return messages
        except ValidationError as err:    
            return err.messages, 400
    @use_kwargs(chat_parsers.message_get_parser(), location= 'query')
    @jwt_required()        
    def get(self, **kwargs):
        current_identity = get_jwt_identity()
        message_list  = chat_utility.read_messages(user= current_identity,
                                                    queryDict= kwargs
                                                 )
        return message_list



