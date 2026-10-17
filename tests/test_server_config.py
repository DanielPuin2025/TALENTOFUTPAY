import unittest

import app


class TestServerConfig(unittest.TestCase):
    def test_default_local_network_host(self):
        host, port = app.get_server_config()
        self.assertEqual(host, '0.0.0.0')
        self.assertEqual(port, 5000)


if __name__ == '__main__':
    unittest.main()
