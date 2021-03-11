import unittest
from base64 import b64decode, b64encode
from json import dumps, loads

from server import app
from src.parameters import get_parameter

app.config['TESTING'] = True


class Test(unittest.TestCase):
    @staticmethod
    def set_login(name: str = 'admin') -> dict:
        with app.test_client() as client:
            response = client.post(
                '/login',
                json={
                    'name': name,
                    'password': get_parameter('first_admin_password')
                }
            )
        return response

    @staticmethod
    def get_login(token: str) -> dict:
        with app.test_client() as client:
            response = client.get(
                '/login',
                headers={'Authorization': 'Bearer ' + token}
            )
        return response

    @staticmethod
    def alterate_token(token: str) -> str:
        t1, t2, t3 = token.split('.')
        payload_dict = loads(b64decode(t2 + '===').decode('utf-8'))
        payload_dict['level'] = 'manager'
        t2 = b64encode(dumps(payload_dict).encode('utf-8')).decode('utf-8')
        return f'{t1}.{t2}.{t3}'

    @staticmethod
    def add_user(token: str, json: dict):
        headers = {'Authorization': 'Bearer ' + token}
        with app.test_client() as client:
            response = client.post('/users', headers=headers, json=json)
        return response

    def check_response(self, response, status_code: int, status: str):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['status'], status)

    def check_response_ok(self, response):
        self.check_response(response, status_code=200, status='ok')

    def check_response_error(self, response, status_code: int):
        self.check_response(response, status_code=status_code, status='error')

    # True TESTS
    def test_login(self):
        self.check_response_ok(self.set_login())

    def test_login_with_wrong_credentials(self):
        self.check_response_error(self.set_login('test'), status_code=401)

    def test_login_info(self):
        response = self.get_login(self.set_login().get_json()['token'])
        self.check_response_ok(response)

    def test_altered_token(self):
        token = self.alterate_token(self.set_login().get_json()['token'])
        self.check_response_error(self.get_login(token), status_code=401)

    def test_add_user(self):
        token = self.set_login().get_json()['token']
        password = get_parameter('first_admin_password')
        response = self.add_user(token, {'name': 'new', 'password': password})
        self.check_response_ok(response)

    def test_add_user_with_lower_role(self):
        token = self.set_login(name='new').get_json()['token']
        response = self.add_user(token, {'name': 'test', 'password': 'test'})
        self.check_response_error(response, status_code=401)

    def test_add_user_has_nonexistent_role(self):
        token = self.set_login().get_json()['token']
        response = self.add_user(token, {'name': 'test', 'role': 'test'})
        self.check_response_error(response, status_code=400)

    def test_add_user_already_existent(self):
        token = self.set_login().get_json()['token']
        response = self.add_user(token, {'name': 'admin'})
        self.check_response_error(response, status_code=409)


if __name__ == '__main__':
    unittest.main()
