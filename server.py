from datetime import datetime
from uuid import uuid4

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from parameters import get_parameter

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


# Combine database add & commit functions
def db_add_and_commit(model: db.Model) -> None:
    db.session.add(model)
    db.session.commit()


# Generate a random hexadecimal value
def random_hex(max_length: int = 6) -> str:
    return uuid4().hex[:max_length]


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=random_hex)
    name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=False,
                     default=list(USER_ROLE.keys())[0])
    since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role
        }


# Create admin user if there are no users in the database
def add_first_admin_user(name: str) -> None:
    if User.query.first() is None:
        password = random_hex(10)
        user = User(name=name, password=password, role='admin')
        db_add_and_commit(user)
        print(f'Admin password: {password}')


@app.route('/')
def index() -> tuple:
    return jsonify([user.to_dict() for user in User.query.all()])


# Commands for initialize the database
db.create_all()
add_first_admin_user(get_parameter('admin_name'))


if __name__ == '__main__':
    app.run(debug=True, port=int(get_parameter('port')))
