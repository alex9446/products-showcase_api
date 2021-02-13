from datetime import datetime

from flask_restful import Resource

from .utils import (db_add_and_commit, db_delete_and_commit, decode_jwt,
                    model_to_dict, random_hex, status_error, status_ok)


# Create admin user if there are no users in the database
def add_first_admin_user(db, User, name: str) -> None:
    if User.query.first() is None:
        password = random_hex(10)
        user = User(name=name, password=password, role='admin')
        db_add_and_commit(db, user)
        print(f'Admin password: {password}')


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

    def delete(self, id: str = None) -> tuple:
        if not self.check_allowed_role('admin'):
            return self.status_user_401()
        user = self.get_first_by_id(id)
        if user:
            db_delete_and_commit(self.db, user)
            return status_ok(user=user.to_dict())
        return self.status_user_404()

    def get(self, id: str = None) -> tuple:
        if not self.check_allowed_role('admin'):
            return self.status_user_401()
        if id:
            user = self.get_first_by_id(id)
            if user:
                return status_ok(user=user.to_dict())
            return self.status_user_404()
        return status_ok(users=model_to_dict(self.User))

    @staticmethod
    def status_user_401() -> tuple:
        return status_error(error_code=401,
                            message='Access denied for your role!')

    @staticmethod
    def status_user_404() -> tuple:
        return status_error(error_code=404, message='User not found!')
