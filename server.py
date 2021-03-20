from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from src.collection import get_Collection_class
from src.login import LoginRest
from src.parameters import get_parameter
from src.product import ProductRest, get_Product_class
from src.user import UserRest, add_first_admin_user, get_User_class

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

# Define many-to-many relationships table
products_collection_table = db.Table(
    'products_collection',
    db.Column('product_id', db.String,
              db.ForeignKey('product.id'), primary_key=True),
    db.Column('collection_id', db.String,
              db.ForeignKey('collection.id'), primary_key=True),
    db.Column('position', db.Integer, nullable=False, default=0)
)

Product = get_Product_class(db, products_collection_table)
Collection = get_Collection_class(db, products_collection_table)

# Commands for initialize the database
db.create_all()
add_first_admin_user(db, User, get_parameter('first_admin_password'))

jwt_secret = get_parameter('jwt_secret')

api.add_resource(LoginRest.add_User(User, jwt_secret),
                 '/login')
api.add_resource(UserRest.add_User(db, User, jwt_secret, USER_ROLE),
                 '/users', '/users/<string:id>')
api.add_resource(ProductRest.add_Product(db, Product, jwt_secret, USER_ROLE),
                 '/products', '/products/<string:id>')


if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True, port=int(get_parameter('port')))
