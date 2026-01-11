"""
Smoke testler - Uygulamanın gerçekten ayağa kalkıp kalkmadığını kontrol eder.
Smoke testler end-to-end testlerdir ve Docker konteynerinin çalıştığını doğrular.
"""

import unittest
import requests
import time


class TestSmoke(unittest.TestCase):
    """Smoke testler - Uygulamanın çalışır durumda olduğunu test eder."""

    def test_health_endpoint(self):
        """
        Health endpoint'in çalıştığını test eder.
        Bu test Docker konteyneri ayağa kalktıktan sonra çalışmalıdır.
        """
        url = "http://localhost:5000/health"
        try:
            response = requests.get(url, timeout=5)
            self.assertEqual(response.status_code, 200, "Health endpoint 200 dönmeli")
            self.assertEqual(response.text.strip(), "OK", "Health endpoint 'OK' dönmeli")
        except requests.exceptions.ConnectionError:
            self.fail("Uygulama çalışmıyor! Docker konteyneri başlatılmış mı?")


if __name__ == '__main__':
    unittest.main()

