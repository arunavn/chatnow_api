from flask import Blueprint
from flask_restful import Api
from flask_jwt_extended import create_access_token,set_access_cookies, get_jwt_identity, jwt_required, get_jwt
from chatnow_api.resources.account_resources import User, Users, Login, ProfilePic
from datetime import timedelta, timezone, datetime
api_bp= Blueprint('account_api', __name__ , url_prefix= '/accounts' )

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

api.add_resource(User, '/user', '/user/<string:value>', '/user/<string:findby>/<string:value>', '/user/<string:findby>/<string:value>/<string:func>')
api.add_resource(Users, '/users', endpoint= 'users')
api.add_resource(Login, '/login', endpoint= 'login')
api.add_resource(ProfilePic, '/profilepic/<string:id>',  endpoint= 'profilepic')

