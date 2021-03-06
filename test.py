import unittest
from base64 import b64decode, b64encode
from json import dumps, loads

from server import app
from src.parameters import get_parameter

app.config['TESTING'] = True


class Test(unittest.TestCase):
    @staticmethod
    def set_login() -> dict:
        with app.test_client() as client:
            response = client.post(
                '/login',
                json={
                    'name': 'admin',
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

    def test_login(self):
        response = self.set_login()
        self.assertEqual(response.status_code, 200)
        response_dict = response.get_json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['token'], str)
        self.assertTrue(len(response_dict['token']) > 0)

    def test_login_info(self):
        response = self.get_login(self.set_login().get_json()['token'])
        self.assertEqual(response.status_code, 200)
        response_dict = response.get_json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['jwt_payload'], dict)
        self.assertEqual(response_dict['jwt_payload']['name'], 'admin')

    def test_altered_token(self):
        token = self.alterate_token(self.set_login().get_json()['token'])
        response = self.get_login(token)
        self.assertEqual(response.status_code, 401)
        response_dict = response.get_json()
        self.assertEqual(response_dict['status'], 'error')
        self.assertEqual(response_dict['message'],
                         'Incorrect account credentials!')


if __name__ == '__main__':
    unittest.main()
