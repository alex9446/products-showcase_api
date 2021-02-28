import unittest

import requests

from src.parameters import get_parameter


def local_server() -> str:
    return 'http://localhost:' + get_parameter('port')


class Test(unittest.TestCase):
    @staticmethod
    def login() -> dict:
        return requests.post(
            url=local_server() + '/login',
            json={
                'name': 'admin',
                'password': get_parameter('first_admin_password')
            }
        )

    def test_login(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['token'], str)
        self.assertTrue(response_dict['token'])

    def test_login_info(self):
        token = self.login().json()['token']
        response = requests.get(
            url=local_server() + '/login',
            headers={'Authorization': 'Bearer ' + token}
        )
        self.assertEqual(response.status_code, 200)
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['jwt_payload'], dict)
        self.assertEqual(response_dict['jwt_payload']['name'], 'admin')


if __name__ == '__main__':
    unittest.main()
