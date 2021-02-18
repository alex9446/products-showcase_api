from datetime import datetime

from flask_restful import Resource, reqparse

from .utils import (db_add_and_commit, db_delete_and_commit, decode_jwt,
                    model_to_dict, random_hex, status_error, status_ok)


# Create admin user if there are no users in the database
def add_first_admin_user(db, User, password: str) -> None:
    if User.query.first() is None:
        user = User(name='admin', password=password, role='admin')
        db_add_and_commit(db, user)
        print(f'Admin name: {user.name}\nAdmin pass: {user.password}')


# Define and return User class model
# Function was needed, because db is required in inheritance
def get_User_class(db, user_role: dict):
    class User(db.Model):
        id = db.Column(db.String, primary_key=True, default=random_hex)
        name = db.Column(db.String, nullable=False, unique=True)
        password = db.Column(db.String, nullable=False)
        first_name = db.Column(db.String, nullable=True)
        last_name = db.Column(db.String, nullable=True)
        role = db.Column(db.String, nullable=False,
                         default=list(user_role.keys())[0])
        since = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        def to_dict(self) -> dict:
            return {
                'id': self.id,
                'name': self.name,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'role': self.role
            }
    return User


# Return User rest resource
class UserRest(Resource):
    @classmethod
    def add_User(cls, db, User, jwt_secret: str, user_role: dict):
        cls.db = db
        cls.User = User
        cls.jwt_secret = jwt_secret
        cls.user_role = user_role
        return cls

    def check_allowed_id(self, id: str) -> bool:
        jwt_payload = decode_jwt(self.jwt_secret)
        if ('id' in jwt_payload) and (jwt_payload['id'] == id):
            return True
        return False

    def check_allowed_role(self, allowed_role: str) -> bool:
        jwt_payload = decode_jwt(self.jwt_secret)
        if 'role' in jwt_payload:
            role_level = self.user_role[jwt_payload['role']]
            allowed_role_level = self.user_role[allowed_role]
            if role_level >= allowed_role_level:
                return True
        return False

    def get_first_by_id(self, id: str):
        return self.User.query.filter_by(id=id).first()

    def get_first_by_name(self, name: str):
        return self.User.query.filter_by(name=name).first()

    def delete(self, id: str = None) -> tuple:
        if not (self.check_allowed_role('admin') or self.check_allowed_id(id)):
            return self.status_user_401()
        user = self.get_first_by_id(id)
        if user:
            db_delete_and_commit(self.db, user)
            return status_ok(user=user.to_dict())
        return self.status_user_404()

    def get(self, id: str = None) -> tuple:
        admin_role = self.check_allowed_role('admin')
        if not (admin_role or self.check_allowed_id(id)):
            return self.status_user_401()
        if id:
            user = self.get_first_by_id(id)
            if user:
                return status_ok(user=user.to_dict())
            return self.status_user_404()
        if admin_role:
            return status_ok(users=model_to_dict(self.User))
        return self.status_user_401()

    def post(self, id: str = None) -> tuple:
        if not self.check_allowed_role('admin'):
            return self.status_user_401()

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, nullable=False)
        parser.add_argument('password', type=str, nullable=False,
                            default=random_hex(10))
        parser.add_argument('first_name', type=str, default=None)
        parser.add_argument('last_name', type=str, default=None)
        parser.add_argument('role', type=str, nullable=False,
                            default=list(self.user_role.keys())[0])
        parsed_values = parser.parse_args()

        if parsed_values['role'] not in self.user_role:
            return self.status_user_400_role()
        if self.get_first_by_name(parsed_values['name']):
            return self.status_user_409()
        user = self.User(**parsed_values)
        db_add_and_commit(self.db, user)
        return status_ok(user=user.to_dict())

    def put(self, id: str = None) -> tuple:
        admin_role = self.check_allowed_role('admin')
        if not (admin_role or self.check_allowed_id(id)):
            return self.status_user_401()
        user = self.get_first_by_id(id)
        if user is None:
            return self.status_user_404()

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, nullable=False,
                            default=user.name)
        parser.add_argument('password', type=str, nullable=False,
                            default=user.password)
        parser.add_argument('first_name', type=str, default=user.first_name)
        parser.add_argument('last_name', type=str, default=user.last_name)
        if admin_role:
            parser.add_argument('role', type=str, nullable=False,
                                default=user.role)
        parsed_values = parser.parse_args()

        if admin_role and (parsed_values['role'] not in self.user_role):
            return self.status_user_400_role()
        if (user.name != parsed_values['name']
           and self.get_first_by_name(parsed_values['name'])):
            return self.status_user_409()
        self.User.query.filter_by(id=id).update(parsed_values)
        self.db.session.commit()
        return status_ok(user=user.to_dict())

    def status_user_400_role(self) -> tuple:
        return status_error(error_code=400, message='Non-existent role!',
                            possible_roles=list(self.user_role.keys()))

    @staticmethod
    def status_user_401() -> tuple:
        return status_error(error_code=401,
                            message='Access denied for your role!')

    @staticmethod
    def status_user_404() -> tuple:
        return status_error(error_code=404, message='User not found!')

    @staticmethod
    def status_user_409() -> tuple:
        return status_error(error_code=409, message='Name already taken!')
