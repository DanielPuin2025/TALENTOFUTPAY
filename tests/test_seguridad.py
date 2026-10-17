import unittest

import app


class TestSeguridad(unittest.TestCase):
    def test_password_fuerte(self):
        self.assertTrue(app.validar_password("Admin123!"))
        self.assertFalse(app.validar_password("admin123"))
        self.assertFalse(app.validar_password("abc"))


if __name__ == "__main__":
    unittest.main()
