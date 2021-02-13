from datetime import datetime, timedelta

from flask_restful import Resource, reqparse
from jwt import encode as jwt_encoder

from .utils import decode_jwt, status_error, status_ok


# Return Login rest resource
class LoginRest(Resource):
    @classmethod
    def add_User(cls, User, jwt_secret: str):
        cls.User = User
        cls.jwt_secret = jwt_secret
        return cls

    def get(self) -> tuple:
        jwt_payload = decode_jwt(self.jwt_secret)
        if jwt_payload:
            return status_ok(jwt_payload=jwt_payload)
        return self.status_auth_401()

    def post(self) -> tuple:
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str,
                            required=True, nullable=False)
        parser.add_argument('password', type=str,
                            required=True, nullable=False)
        parsed_values = parser.parse_args()

        name, password = (parsed_values['name'], parsed_values['password'])
        user = self.User.query.filter_by(name=name, password=password).first()
        if user:
            jwt_payload = user.to_dict()
            jwt_payload['exp'] = datetime.utcnow() + timedelta(days=30)
            token = jwt_encoder(jwt_payload, self.jwt_secret,
                                algorithm='HS256')
            return status_ok(token=token)
        return self.status_auth_401()

    @staticmethod
    def status_auth_401() -> tuple:
        return status_error(error_code=401,
                            message='Incorrect account credentials!')
