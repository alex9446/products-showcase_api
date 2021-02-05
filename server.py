from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from src.parameters import get_parameter
from src.user import add_first_admin_user, get_User_class
from src.utils import model_to_dict

app = Flask(__name__)

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


@app.route('/')
def index() -> tuple:
    return jsonify(model_to_dict(User))


if __name__ == '__main__':
    app.run(debug=True, port=int(get_parameter('port')))
