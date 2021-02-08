from flask_restful import Resource, reqparse
from jwt import encode as jwt_encoder


# Return Login rest resource
class LoginRest(Resource):
    @classmethod
    def add_User(cls, User, jwt_secret):
        cls.User = User
        cls.jwt_secret = jwt_secret
        return cls

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str,
                            required=True, nullable=False)
        parser.add_argument('password', type=str,
                            required=True, nullable=False)
        parsed_values = parser.parse_args()

        name, password = (parsed_values['name'], parsed_values['password'])
        user = self.User.query.filter_by(name=name, password=password).first()
        if user:
            token = jwt_encoder(user.to_dict(), self.jwt_secret)
            return {'token': token}
        return {}, 401
