from flask import Blueprint
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token,set_access_cookies, get_jwt_identity, jwt_required, get_jwt
from chatnow_api.resources.chat_resources import Chats, People, Messages
from datetime import timedelta, timezone, datetime
api_bp= Blueprint('chat_api', __name__ , url_prefix= '/' )

api= Api(api_bp)
@api_bp.after_request
def refresh_token(response):
    try:
        current_identity= get_jwt_identity()
        if current_identity:
            exp_timestamp= get_jwt()['exp']
            now= datetime.now(timezone.utc)
            target_timestamp= datetime.timestamp( now + timedelta(minutes= 30))
            if target_timestamp > exp_timestamp:
                access_token= create_access_token(identity= current_identity)
                set_access_cookies(response, access_token)
        return response
    except(RuntimeError, KeyError):
        return response

api.add_resource(Messages, '/messages', endpoint= 'messages')
api.add_resource(Chats, '/chats')
api.add_resource(People, '/people')