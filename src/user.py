from datetime import datetime

from .utils import db_add_and_commit, random_hex


# Create admin user if there are no users in the database
def add_first_admin_user(db, User, name: str) -> None:
    if User.query.first() is None:
        password = random_hex(10)
        user = User(name=name, password=password, role='admin')
        db_add_and_commit(db, user)
        print(f'Admin password: {password}')


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
