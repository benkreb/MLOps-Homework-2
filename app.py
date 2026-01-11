"""
Ana Flask uygulaması - MLOps Homework
"""

from flask import Flask, request, jsonify
from feature_engineering import hash_feature

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - Smoke test için kullanılır.
    """
    return "OK", 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint - Feature engineering ile entegrasyon testi için.
    Component test bu endpoint'i kullanarak model serving logic ile
    feature engineering arasındaki etkileşimi doğrular.
    """
    try:
        data = request.get_json()
        if not data or 'feature_value' not in data:
            return jsonify({'error': 'feature_value is required'}), 400
        
        feature_value = data['feature_value']
        num_buckets = data.get('num_buckets', 10)
        
        # Feature engineering kullanarak hash feature oluştur
        hashed_feature = hash_feature(feature_value, num_buckets)
        
        return jsonify({
            'hashed_feature': hashed_feature,
            'input_value': feature_value,
            'num_buckets': num_buckets
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

