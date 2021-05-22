from flask_restful import reqparse
from webargs import fields, validate

def userdata_post_parser():
    parser= reqparse.RequestParser()
    parser.add_argument('id')
    parser.add_argument( 'userid', required= True )
    parser.add_argument( 'email', required= True )
    parser.add_argument( 'name', required= True )
    parser.add_argument( 'password', required= True )
    parser.add_argument( 'about', required= False )
    return parser

def userdata_patch_parser():
    parser= reqparse.RequestParser()
    parser.add_argument('id')
    parser.add_argument( 'userid')
    parser.add_argument( 'email' )
    parser.add_argument( 'name' )
    parser.add_argument( 'password' )
    parser.add_argument( 'cnfpassword' )
    parser.add_argument( 'newpassword' )
    parser.add_argument( 'about' )
    return parser

def user_get_parser():
    user_args = {
        'id': fields.Str(),
        'userid': fields.Str(),
        'email': fields.Str()
    }
    return user_args
def user_login_parser():
    user_args = {
        'userid': fields.Str(required=True),
        'password': fields.Str(required=True)
    }
    return user_args