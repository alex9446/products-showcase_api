import unittest

import requests

from src.parameters import get_parameter


def local_server() -> str:
    return 'http://localhost:' + get_parameter('port')


class Test(unittest.TestCase):
    def test_login(self):
        response = requests.post(
            url=local_server() + '/login',
            json={
                'name': 'admin',
                'password': get_parameter('first_admin_password')
            }
        )
        response_dict = response.json()
        self.assertEqual(response_dict['status'], 'ok')
        self.assertIsInstance(response_dict['token'], str)
        self.assertTrue(response_dict['token'])


if __name__ == '__main__':
    unittest.main()
