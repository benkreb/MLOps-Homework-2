"""
Feature engineering functions for MLOps homework.
"""


def hash_feature(value, num_buckets=10):
    """
    Basit bir hashleme fonksiyonu.
    
    Args:
        value: Hashlenecek değer
        num_buckets: Bucket sayısı (varsayılan: 10)
    
    Returns:
        int: 0 ile num_buckets-1 arasında bir değer
    """
    return hash(value) % num_buckets
