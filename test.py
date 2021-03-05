import unittest
from base64 import b64decode, b64encode
from json import dumps, loads

import requests

from src.parameters import get_parameter


def local_server() -> str:
    return 'http://localhost:' + get_parameter('port')


class Test(unittest.TestCase):
    @staticmethod
    def set_login() -> dict:
        return requests.post(
            url=local_server() + '/login',
            json={
                'name': 'admin',
                'password': get_parameter('first_admin_password')
            }
        )

    @staticmethod
    def get_login(token: str) -> dict:
        return requests.get(
            url=local_server() + '/login',
            headers={'Authorization': 'Bearer ' + token}
        )

    @staticmethod
    def alterate_token(token: str) -> str:
        t1, t2, t3 = token.split('.')
        payload_dict = loads(b64decode(t2 + '==='))
        payload_dict['level'] = 'manager'
        t2 = b64encode(dumps(payload_dict).encode('utf-8')).decode('utf-8')
        return f'{t1}.{t2}.{t3}'

    def test_login(self):
        response = self.set_login()
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['token'], str)
        self.assertTrue(response_dict['token'])

    def test_login_info(self):
        response = self.get_login(self.set_login().json()['token'])
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['jwt_payload'], dict)
        self.assertEqual(response_dict['jwt_payload']['name'], 'admin')

    def test_altered_token(self):
        token = self.alterate_token(self.set_login().json()['token'])
        response = self.get_login(token)
        self.assertEqual(response.status_code, 401)
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'error')
        self.assertIsInstance(response_dict['message'], str)


if __name__ == '__main__':
    unittest.main()
