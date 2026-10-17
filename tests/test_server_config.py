import unittest

import app


class TestServerConfig(unittest.TestCase):
    def test_default_local_network_host(self):
        host, port = app.get_server_config()
        self.assertEqual(host, '0.0.0.0')
        self.assertEqual(port, 5000)

    def test_health_check_is_public(self):
        response = app.app.test_client().get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {'status': 'ok', 'app': 'talentofutpay'})


if __name__ == '__main__':
    unittest.main()
