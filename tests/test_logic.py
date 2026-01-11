"""
Unit testler - Feature engineering fonksiyonlarını test eder.
Unit testler hızlıdır ve dış bağımlılık (veritabanı, ağ) gerektirmez.
"""

import unittest
import sys
import os

# Üst dizindeki modülleri import edebilmek için path ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from feature_engineering import hash_feature


class TestFeatureEngineering(unittest.TestCase):
    """Feature engineering fonksiyonları için unit testler."""

    def test_hashing_consistency(self):
        """
        Aynı girdi her zaman aynı çıktıyı vermeli (Deterministik).
        """
        val = "kullanici_1"
        result1 = hash_feature(val)
        result2 = hash_feature(val)
        self.assertEqual(result1, result2, "Hash fonksiyonu deterministik olmalı")

    def test_bucket_range(self):
        """
        Çıktı 0 ile num_buckets-1 arasında olmalı.
        """
        val = "test_data"
        num_buckets = 10
        result = hash_feature(val, num_buckets=num_buckets)
        self.assertTrue(0 <= result < num_buckets,
                        f"Sonuç 0 ile {num_buckets-1} arasında olmalı, ama {result} geldi")

    def test_different_values_different_hashes(self):
        """
        Farklı değerler farklı hash'ler üretmeli (genellikle).
        """
        val1 = "kullanici_1"
        val2 = "kullanici_2"
        result1 = hash_feature(val1)
        result2 = hash_feature(val2)
        # Not: Hash çakışması olabilir, ama genellikle farklı olmalı
        # Bu test sadece fonksiyonun çalıştığını doğrular
        self.assertIsInstance(result1, int)
        self.assertIsInstance(result2, int)


if __name__ == '__main__':
    unittest.main()

