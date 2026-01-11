"""
Component/Integration testler - Model serving logic ile feature engineering
arasındaki etkileşimi test eder.
Component testler unit testlerden farklı olarak, farklı bileşenlerin
birbirleriyle nasıl etkileşime girdiğini doğrular.
Bu test, app.py (model serving) ile feature_engineering.py arasındaki
entegrasyonu test eder.
"""

import unittest
import sys
import os

# Üst dizindeki modülleri import edebilmek için path ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from feature_engineering import hash_feature


class TestComponentIntegration(unittest.TestCase):
    """
    Component/Integration testler - app.py ile feature_engineering.py
    arasındaki etkileşimi test eder.
    """

    def setUp(self):
        """Her test öncesi Flask test client'ı oluştur."""
        self.client = app.test_client()
        self.client.testing = True

    def test_prediction_endpoint_integration(self):
        """
        Prediction endpoint'in feature_engineering modülü ile
        doğru şekilde entegre olduğunu test eder.
        Bu bir component testtir çünkü iki farklı bileşenin
        (app.py ve feature_engineering.py) birlikte çalışmasını doğrular.
        """
        test_data = {
            'feature_value': 'test_user_123',
            'num_buckets': 10
        }
        
        # API endpoint'e POST isteği gönder
        response = self.client.post('/predict',
                                   json=test_data,
                                   content_type='application/json')
        
        # HTTP 200 OK kontrolü
        self.assertEqual(response.status_code, 200,
                        "Prediction endpoint 200 OK dönmeli")
        
        # JSON response kontrolü
        result = response.get_json()
        self.assertIsNotNone(result, "Response JSON olmalı")
        self.assertIn('hashed_feature', result,
                     "Response'da hashed_feature olmalı")
        
        # Feature engineering fonksiyonunu doğrudan çağırarak
        # sonucun doğru olduğunu doğrula
        expected_hash = hash_feature(test_data['feature_value'],
                                    test_data['num_buckets'])
        self.assertEqual(result['hashed_feature'], expected_hash,
                        "API response'daki hash değeri feature_engineering "
                        "fonksiyonunun sonucuyla eşleşmeli")
        
        # Input değerlerinin doğru şekilde döndüğünü kontrol et
        self.assertEqual(result['input_value'], test_data['feature_value'])
        self.assertEqual(result['num_buckets'], test_data['num_buckets'])

    def test_prediction_endpoint_validation(self):
        """
        Prediction endpoint'in hatalı input'lara doğru şekilde
        yanıt verdiğini test eder (validation test).
        """
        # Eksik feature_value ile istek gönder
        invalid_data = {'num_buckets': 10}
        
        response = self.client.post('/predict',
                                   json=invalid_data,
                                   content_type='application/json')
        
        # HTTP 400 Bad Request kontrolü
        self.assertEqual(response.status_code, 400,
                        "Geçersiz input için 400 dönmeli")
        
        result = response.get_json()
        self.assertIn('error', result, "Hata mesajı dönmeli")

    def test_prediction_endpoint_with_different_buckets(self):
        """
        Farklı bucket sayılarıyla prediction endpoint'in
        doğru çalıştığını test eder.
        """
        test_cases = [
            {'feature_value': 'user_1', 'num_buckets': 5},
            {'feature_value': 'user_2', 'num_buckets': 20},
            {'feature_value': 'user_3', 'num_buckets': 100},
        ]
        
        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                response = self.client.post('/predict',
                                           json=test_data,
                                           content_type='application/json')
                
                self.assertEqual(response.status_code, 200)
                result = response.get_json()
                
                # Hash değeri bucket aralığında olmalı
                self.assertGreaterEqual(result['hashed_feature'], 0)
                self.assertLess(result['hashed_feature'], test_data['num_buckets'])


if __name__ == '__main__':
    unittest.main()
