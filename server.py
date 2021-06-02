from flask import Flask, redirect
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from src.login import LoginRest
from src.parameters import get_parameter
from src.product import ProductRest, get_Product_class, get_ProductImages_class
from src.user import UserRest, add_first_admin_user, get_User_class
from src.utils import status_error

app = Flask(__name__)

app.config['BUNDLE_ERRORS'] = True  # For bundle the errors of RequestParser
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
Product = get_Product_class(db)
ProductImages = get_ProductImages_class(db)

# Commands for initialize the database
db.create_all()
add_first_admin_user(db, User, get_parameter('first_admin_password'))

jwt_secret = get_parameter('jwt_secret')


@app.route('/')
def index() -> tuple:
    return redirect(get_parameter('redirect_url'), code=301)


# Return error 404 as JSON
@app.errorhandler(404)
def page_not_found(e) -> tuple:
    return status_error(error_code=404, message='Page not found!')


# Declaration of the allowed cors requests
allowed_cors = get_parameter('allowed_cors')
if allowed_cors:
    CORS(app, resources={
        r'^\/(login|users|products).*': {
            'origins': allowed_cors
        }
    })

# Declaration of the REST endpoints
api.add_resource(LoginRest.add_User(User, jwt_secret),
                 '/login')
api.add_resource(UserRest.add_User(db, User, jwt_secret, USER_ROLE),
                 '/users', '/users/<string:id>')
api.add_resource(ProductRest.add_Product(db, Product, ProductImages,
                                         jwt_secret, USER_ROLE),
                 '/products', '/products/<string:id>')


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True, port=int(get_parameter('port')))
