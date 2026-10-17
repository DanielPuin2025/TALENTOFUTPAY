import unittest

import app


class TestWhatsAppReminder(unittest.TestCase):
    def test_generates_whatsapp_for_pending_payment(self):
        jugadora = {
            "nombre": "Ana Gómez",
            "acudiente_nombre": "María Gómez",
            "acudiente_telefono": "3001234567",
        }

        enlace = app.enlace_recordatorio_pago(jugadora, "Mayo", 50000)

        self.assertIsNotNone(enlace)
        self.assertIn("wa.me/573001234567", enlace)
        self.assertIn("Ana%20G%C3%B3mez", enlace)


if __name__ == "__main__":
    unittest.main()
