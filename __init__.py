from flask import Flask,request, redirect, make_response
from flask_jwt_extended import JWTManager
import os
from flask import request
from flask_cors import CORS
from webargs.flaskparser import use_args, use_kwargs
from webargs import fields
from datetime import timedelta
from flask_mail import Mail
from celery import Celery
def create_app(test_config= None):
    app= Flask(__name__, instance_relative_config= True)
    jwt= JWTManager(app)
    # CORS(app, resources= { r"/*": { "support_credential" : True, "origins" :'http://127.0.0.1:8000/'} })
    app.config['SECRET_KEY']= 'super-secret'
    app.config['JWT_SECRET_KEY']= 'secret-secret'
    app.config["JWT_TOKEN_LOCATION"] = [ "cookies"]
    app.config["JWT_COOKIE_SECURE"] = False
    app.config['JWT_ACCESS_COOKIE_NAME']= "access_token_cookie"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    #email
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] =  'an.appstest@gmail.com'
    app.config['MAIL_PASSWORD'] =  'Hello@81111'
    
    #celery
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    app.config['UPLOAD_FILE_PATH'] = os.path.join(app.root_path, 'uploads')
    app.config['PP_FILE_PATH'] = os.path.join(app.config['UPLOAD_FILE_PATH'], 'profilepics' )

    mail = Mail(app)
    #celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

    if test_config is None:
        app.config.from_pyfile('config.py', silent= True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    try:
        os.makedirs(app.config['UPLOAD_FILE_PATH'])
    except OSError:
        pass

    try:
        os.makedirs(app.config['PP_FILE_PATH'])
    except OSError:
        pass
    @use_kwargs({'redirecturl': fields.Str(),'accesskey': fields.Str()}, location= 'query')
    @app.route('/setcookie')
    def hello(**kwargs):
        access_token_cookie= kwargs.get('accesskey', '')
        redirecturl= kwargs.get('redirecturl', '')
        resp= make_response(redirect(redirecturl))
        resp.set_cookie('access_token_cookie1', access_token_cookie)
        return resp

    from chatnow_api.database import db_session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    @app.after_request
    def add_header(response):
       print(request.environ.get('HTTP_ORIGIN', ''))
       response.headers['Access-Control-Allow-Origin'] = request.environ.get('HTTP_ORIGIN', '')
       response.headers['Access-Control-Allow-Headers'] = 'X-CSRF-TOKEN,Content-Type,Access-Control-Allow-Origin'
       response.headers['Access-Control-Allow-Credentials'] = 'true'
       response.headers['Access-Control-Allow-Methods'] = 'POST,PATCH,GET,DELETE'
       return response

    from chatnow_api.database import init_db
    init_db()
      
    from . import accounts
    app.register_blueprint(accounts.api_bp)
    from . import chat
    app.register_blueprint(chat.api_bp)
    return app



