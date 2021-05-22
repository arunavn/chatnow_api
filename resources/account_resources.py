from flask_restful import Resource
from chatnow_api.utilities.common.utility_functions import generate_password
from flask import jsonify, request, make_response, send_file, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from webargs.flaskparser import use_args, use_kwargs
from chatnow_api.utilities.user import user_utility, user_parsers
import os
from webargs import fields


class Login(Resource):
    @use_args(user_parsers.user_login_parser(), location='json')
    def post(self, args):
        ret_user= user_utility.get_user(findby= 'userid', value= args['userid'], hidePassword=False, hidePersonal= False)
        if ret_user.pStatus != 'E' and ret_user.data.password == args['password']:
            response = jsonify([{"msg": "login successful"}])
            access_token= create_access_token((ret_user.data).id)
            #jsonify(response).set_cookie('access_token_cookie', access_token)
            set_access_cookies(response, access_token)
            return response
        else:
            return { 'msg:':'Incorrect password'}, 405


class Users(Resource):
    #@jwt_required()
    @use_kwargs(user_parsers.user_get_parser(), location= 'query')
    def get(self, **kwargs):
        _id= kwargs.get('id', None)
        email= kwargs.get('email', None)
        userid= kwargs.get('userid', None)
        ret_users= user_utility.get_users(_id, userid, email)
        if ret_users.pStatus == 'E':
            return {'message':ret_users.pMessage   }, 404
        return jsonify([u.__dict__ for u in ret_users.data])


    
class User(Resource):
    @jwt_required(optional=True)
    def get(self, value=None, findby=None, func= None):
        current_identity= get_jwt_identity()
        if current_identity:
            if findby is None and value is None:
                findby = 'id'
                value = current_identity
            ret_user= user_utility.get_user(findby, value, hidePersonal= False)
        else:
            ret_user= user_utility.get_user(findby, value, func= func)
        if ret_user.pStatus == 'E':
            return {'message':ret_user.pMessage   }, 404
        return jsonify( (ret_user.data).__dict__ )

    def post(self, value=None, findby=None, func= None):
        args= user_parsers.userdata_post_parser().parse_args()
        posted_user = user_utility.post_user(args)
        if posted_user.pStatus != 'E':
            return (posted_user.data).__dict__ , 201
        return {'message':posted_user.pMessage   }, 400
        
    @jwt_required(optional= True)
    def patch(self, value=None, findby=None, func= None):
        args= user_parsers.userdata_patch_parser().parse_args()
        current_identity= get_jwt_identity()
        if current_identity and func in ['update', None]:
            ret_user= user_utility.get_user(findby, value)
            if ret_user.data is None or ret_user.data.id != current_identity:
                return '', 401
        patched_user = user_utility.patch_user(findby, value, args, func)
        if patched_user.pStatus != 'E':
            return (patched_user.data).__dict__, 204
        return {'message':patched_user.pMessage   }, 400

    @jwt_required()
    def delete(self, value=None, findby=None, func= None):
        current_user= get_jwt_identity()
        ret_user= user_utility.get_user(findby, value)
        if ret_user.data is None or ret_user.data.id != current_user:
            return '', 401
        deleted_user= user_utility.delete_user(findby, value)
        if deleted_user.pStatus != 'E':
            return '', 204
        return {'message':deleted_user.pMessage   }, 404
class ProfilePic(Resource):
    def patch(self, id):
        allowed_ext= ['jpg', 'png', 'jpeg']
        extn= (request.files['file'].filename).split('.')[-1]
        if extn.lower() not in allowed_ext:
            return "invalid file format", 400
        self.delete(id)
        filename= os.path.join(current_app.config['PP_FILE_PATH'], '{}.{}'.format(id, extn.lower()))
        request.files['file'].save(filename)
        return "", 204
    @jwt_required()
    @use_kwargs({'version': fields.Str()}, location= 'query')
    def get(self, id, **kwargs):
        allowed_ext= ['jpg', 'png', 'jpeg']
        for extn in allowed_ext:
            try:
                op_filename = id + generate_password()
                filename= os.path.join(current_app.config['PP_FILE_PATH'], '{}.{}'.format(id, extn))
                response = send_file(
                filename_or_fp=filename,
                mimetype="image/{}".format(extn),
                as_attachment=True,
                attachment_filename= '{}.{}'.format(op_filename, extn)
                )
                return response
            except:
                pass
        return '', 204
        
    def delete(self, id):
        allowed_ext= ['jpg', 'png', 'jpeg']
        for extn in allowed_ext:
            filename= os.path.join(current_app.config['PP_FILE_PATH'], '{}.{}'.format(id, extn))
            try:
                os.remove(filename)
            except:
                pass
        return '', 204

        


        



