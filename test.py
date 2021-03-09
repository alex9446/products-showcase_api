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

    def check_response(self, response,
                       status_code: int = 200, status: str = 'ok'):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get_json()['status'], status)

    def check_incorrect_ac(self, response):
        self.check_response(response, status_code=401, status='error')
        self.assertEqual(response.get_json()['message'],
                         'Incorrect account credentials!')

    def check_access_denied(self, response):
        self.check_response(response, status_code=401, status='error')
        self.assertEqual(response.get_json()['message'],
                         'Access denied for your role!')

    def test_login(self):
        response = self.set_login()
        self.check_response(response)
        token = response.get_json()['token']
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_login_with_wrong_credentials(self):
        self.check_incorrect_ac(self.set_login('test'))

    def test_login_info(self):
        response = self.get_login(self.set_login().get_json()['token'])
        self.check_response(response)
        jwt_payload = response.get_json()['jwt_payload']
        self.assertIsInstance(jwt_payload, dict)
        self.assertEqual(jwt_payload['name'], 'admin')

    def test_altered_token(self):
        token = self.alterate_token(self.set_login().get_json()['token'])
        self.check_incorrect_ac(self.get_login(token))

    def test_add_user(self):
        token = self.set_login().get_json()['token']
        password = get_parameter('first_admin_password')
        response = self.add_user(token, {'name': 'new', 'password': password})
        self.check_response(response)
        user = response.get_json()['user']
        self.assertIsInstance(user, dict)
        self.assertEqual(user['name'], 'new')

    def test_add_user_with_lower_role(self):
        token = self.set_login(name='new').get_json()['token']
        response = self.add_user(token, {'name': 'test', 'password': 'test'})
        self.check_access_denied(response)


if __name__ == '__main__':
    unittest.main()
