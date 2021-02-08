from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from src.login import LoginRest
from src.parameters import get_parameter
from src.user import UserRest, add_first_admin_user, get_User_class
from src.utils import random_hex

app = Flask(__name__)

api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = get_parameter('database_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress logged warning
db = SQLAlchemy(app)

# Define users role level
USER_ROLE = {
    'viewer': 0,
    'unscrambler': 20,
    'manager': 40,
    'admin': 60
}

User = get_User_class(db, USER_ROLE)

# Commands for initialize the database
db.create_all()
add_first_admin_user(db, User, get_parameter('admin_name'))

jwt_secret = random_hex(20)

api.add_resource(LoginRest.add_User(User, jwt_secret), '/login')
api.add_resource(UserRest.add_User(db, User), '/users', '/users/<string:id>')


if __name__ == '__main__':
    app.run(debug=True, port=int(get_parameter('port')))
