from flask import Blueprint
from flask_restplus import Api

from app.main.controller.auth import api as auth_ns
from app.main.controller.user import api as user_ns

blueprint = Blueprint('api', __name__)

api = Api(
    blueprint,
    title='Flask-RESTPlus API boiler-plate with JWT',
    version='1.0',
    description='A boilerplate for Flask-RESTPlus web service'
)

api.add_namespace(auth_ns)
api.add_namespace(user_ns, path='/users')
