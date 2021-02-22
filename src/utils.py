from uuid import uuid4

from flask_restful import reqparse
from jwt import decode as jwt_decoder
from jwt import exceptions as jwt_exceptions


# Check if the user role is enough
def check_allowed_role(allowed_role: str,
                       jwt_secret: str,
                       user_role: dict) -> bool:
    jwt_payload = decode_jwt(jwt_secret)
    if 'role' in jwt_payload:
        role_level = user_role[jwt_payload['role']]
        allowed_role_level = user_role[allowed_role]
        if role_level >= allowed_role_level:
            return True
    return False


# Combine database add & commit functions
def db_add_and_commit(db, model) -> None:
    db.session.add(model)
    db.session.commit()


# Combine database delete & commit functions
def db_delete_and_commit(db, model) -> None:
    db.session.delete(model)
    db.session.commit()


# Decode a JSON Web Token encapsulated in the Authorization: Bearer
def decode_jwt(jwt_secret: str) -> dict:
    parser = reqparse.RequestParser()
    parser.add_argument('Authorization', type=str,
                        required=True, nullable=False, location='headers')
    only_token = parser.parse_args()['Authorization'].replace('Bearer ', '')
    try:
        return jwt_decoder(only_token, jwt_secret, algorithms=['HS256'])
    except jwt_exceptions.InvalidTokenError:
        return {}


# Get model as a list of dictionaries
def model_to_dict(model) -> list:
    return [row.to_dict() for row in model.query.all()]


# Generate a random hexadecimal value
def random_hex(max_length: int = 6) -> str:
    return uuid4().hex[:max_length]


def status_ok(**kwargs) -> tuple:
    response = kwargs
    response['status'] = 'ok'
    return response, 200


def status_error(error_code: int, message: str = '', **kwargs) -> tuple:
    response = kwargs
    response['message'] = message
    response['status'] = 'error'
    return response, error_code


def status_user_401() -> tuple:
    return status_error(error_code=401, message='Access denied for your role!')
