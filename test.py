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
    def payload_encode(json: dict) -> str:
        return b64encode(dumps(json).encode('utf-8')).decode('utf-8')

    @staticmethod
    def payload_decode(json: str) -> dict:
        return loads(b64decode(json + '===').decode('utf-8'))

    def alterate_token(self, token: str) -> str:
        t1, t2, t3 = token.split('.')
        payload_dict = self.payload_decode(t2)
        payload_dict['level'] = 'manager'
        t2 = self.payload_encode(payload_dict)
        return f'{t1}.{t2}.{t3}'

    @staticmethod
    def add_user(token: str, json: dict):
        headers = {'Authorization': 'Bearer ' + token}
        with app.test_client() as client:
            response = client.post('/users', headers=headers, json=json)
        return response

    @staticmethod
    def edit_user(token: str, user_id: str, json: dict):
        headers = {'Authorization': 'Bearer ' + token}
        with app.test_client() as client:
            response = client.put('/users/' + user_id,
                                  headers=headers, json=json)
        return response

    @staticmethod
    def get_user(token: str, user_id: str = None):
        headers = {'Authorization': 'Bearer ' + token}
        with app.test_client() as client:
            response = (client.get('/users/' + user_id, headers=headers)
                        if user_id else client.get('/users', headers=headers))
        return response

    @staticmethod
    def delete_user(token: str, user_id: str):
        headers = {'Authorization': 'Bearer ' + token}
        with app.test_client() as client:
            response = client.delete('/users/' + user_id, headers=headers)
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

    def test_edit_user(self):
        token = self.set_login().get_json()['token']
        user_id = self.payload_decode(token.split('.')[1])['id']
        response = self.edit_user(token, user_id, {'first_name': 'Test'})
        self.check_response_ok(response)

    def test_edit_user_password(self):
        token = self.set_login().get_json()['token']
        user = self.add_user(token, {'name': 'pwd'}).get_json()['user']
        response = self.edit_user(token, user['id'], {'password': 'pwd'})
        self.check_response_ok(response)

    def test_edit_user_with_lower_role(self):
        admin_token = self.set_login().get_json()['token']
        user_id = self.payload_decode(admin_token.split('.')[1])['id']
        token = self.set_login(name='new').get_json()['token']
        response = self.edit_user(token, user_id, {'name': 'test'})
        self.check_response_error(response, status_code=401)

    def test_edit_nonexistent_user(self):
        token = self.set_login().get_json()['token']
        response = self.edit_user(token, '000000', {'name': 'test'})
        self.check_response_error(response, status_code=404)

    def test_edit_user_has_nonexistent_role(self):
        token = self.set_login().get_json()['token']
        user_id = self.payload_decode(token.split('.')[1])['id']
        response = self.edit_user(token, user_id,
                                  {'name': 'test', 'role': 'test'})
        self.check_response_error(response, status_code=400)

    def test_edit_user_already_existent(self):
        token = self.set_login().get_json()['token']
        user_id = self.payload_decode(token.split('.')[1])['id']
        self.add_user(token, {'name': 'existent'})
        response = self.edit_user(token, user_id, {'name': 'existent'})
        self.check_response_error(response, status_code=409)

    def test_get_user(self):
        token = self.set_login().get_json()['token']
        new_user = self.add_user(token, {'name': 'get'}).get_json()['user']
        response = self.get_user(token, new_user['id'])
        self.check_response_ok(response)

    def test_get_all_users(self):
        token = self.set_login().get_json()['token']
        response = self.get_user(token)
        self.check_response_ok(response)

    def test_get_user_with_lower_role(self):
        token = self.set_login(name='new').get_json()['token']
        response = self.get_user(token)
        self.check_response_error(response, status_code=401)

    def test_get_nonexistent_user(self):
        token = self.set_login().get_json()['token']
        response = self.get_user(token, '000000')
        self.check_response_error(response, status_code=404)

    def test_delete_user(self):
        token = self.set_login().get_json()['token']
        new_user = self.add_user(token, {'name': 'delete'}).get_json()['user']
        response = self.delete_user(token, new_user['id'])
        self.check_response_ok(response)

    def test_delete_user_with_lower_role(self):
        token = self.set_login(name='new').get_json()['token']
        response = self.delete_user(token, '000000')
        self.check_response_error(response, status_code=401)

    def test_delete_nonexistent_user(self):
        token = self.set_login().get_json()['token']
        response = self.delete_user(token, '000000')
        self.check_response_error(response, status_code=404)

    def test_delete_user_with_same_user(self):
        token = self.set_login().get_json()['token']
        password = get_parameter('first_admin_password')
        new_user = self.add_user(
            token, {'name': 'delete', 'password': password}
        ).get_json()['user']
        new_user_token = self.set_login(name='delete').get_json()['token']
        print(new_user_token)
        response = self.delete_user(new_user_token, new_user['id'])
        self.check_response_ok(response)


if __name__ == '__main__':
    unittest.main()
