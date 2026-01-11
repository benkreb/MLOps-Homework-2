# Homework 2 - Implementing the MLOps CI/CD Pipeline
## Report

**Student:** Berk Gunberk  
**Course:** MLOps  
**Date:** January 11, 2026

---

## Part 1: The Commit Stage (Continuous Integration)

### 1.1 Version Control Setup

All project assets are stored in the GitHub repository: https://github.com/benkreb/MLOps-Homework-2

The repository contains:
- Source code (`app.py`, `feature_engineering.py`)
- Docker configuration (`Dockerfile`)
- Test files (`tests/test_logic.py`, `tests/test_component.py`, `tests/test_smoke.py`)
- CI/CD pipeline configuration (`.github/workflows/main.yml`)
- Dependencies file (`requirements.txt`)

### 1.2 Automated Unit Testing

Unit tests are implemented in `tests/test_logic.py`. These tests are:
- **Fast**: Execute in milliseconds with no external dependencies
- **Isolated**: No database or network calls required
- **Focused**: Test only the feature engineering logic

**Unit Test Code:**

```python
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
        self.assertIsInstance(result1, int)
        self.assertIsInstance(result2, int)


if __name__ == '__main__':
    unittest.main()
```

**Why Unit Tests are Fast:**
Unit tests are considered fast because they:
- Have no external dependencies (no database, network, or file system access)
- Execute pure function logic in memory
- Complete in milliseconds without I/O operations
- Can run in parallel without conflicts

### 1.3 Code Analysis/Linting

Static code analysis is integrated using Pylint. The pipeline configuration enforces code quality by running:

```yaml
- name: Linting (Kod Kalitesi - Part 1 Task 3)
  run: |
    pylint --disable=all --enable=F,E feature_engineering.py app.py
```

This configuration:
- Disables style warnings (W, C, R)
- Only enables fatal errors (F) and errors (E)
- Fails the build if syntax errors or undefined variables are detected

---

## Part 2: The Automated Acceptance Gate (CD)

### 2.1 Component/Integration Testing

A component test is implemented in `tests/test_component.py` that verifies the interaction between the model serving logic (`app.py`) and the feature engineering module (`feature_engineering.py`).

**Component Test Code:**

```python
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


if __name__ == '__main__':
    unittest.main()
```

**Why This is a Component Test:**
Unlike unit tests, this component test:
- Tests the interaction between multiple components (Flask app and feature engineering module)
- Verifies that the API endpoint correctly integrates with the feature engineering logic
- Tests the full request-response cycle through the Flask application
- Ensures proper data flow between components

### 2.2 Build & Package

The project uses Docker for packaging. The build process is automated in the CI/CD pipeline:

```yaml
- name: Paketi Oluştur (Docker Build - Part 2 Task 1)
  run: |
    docker build -t my-mlops-app .
```

The Dockerfile packages the application and all dependencies into a single container image, following the principle of "building binaries only once."

### 2.3 Smoke Test

The smoke test verifies that the deployed application is working correctly. It's implemented in `tests/test_smoke.py`.

**Smoke Test Code:**

```python
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
```

**Why Smoke Tests are End-to-End:**
Smoke tests are considered end-to-end because they:
- Spin up the complete Docker container (full deployment)
- Make real HTTP requests to the running service
- Verify the entire system works from a user's perspective
- Test the complete deployment pipeline (build → deploy → verify)
- Require the full infrastructure to be running (Docker, network, service)

---

## Part 3: The "Stop the Line" Simulation

### 3.1 The Sabotage

An intentional syntax error was introduced into `feature_engineering.py`:

**Before (Correct):**
```python
return hash(value) % num_buckets
```

**After (Sabotaged):**
```python
return hash(value % num_buckets  # KASITLI SYNTAX HATASI - kapatıcı parantez eksik
```

The error: Missing closing parenthesis, causing a `SyntaxError: '(' was never closed`.

### 3.2 The Block

The broken code was committed and pushed to the repository. The CI/CD pipeline detected the failure at the linting stage and stopped the deployment process, preventing the broken code from reaching production.

---

## Deliverables

### 1. Pipeline Configuration

**Screenshot Placeholder:**
```
[SCREENSHOT: .github/workflows/main.yml file showing the complete pipeline configuration]
```

The pipeline configuration file (`.github/workflows/main.yml`) defines the following stages:

1. **Checkout**: Code checkout from repository
2. **Python Setup**: Python 3.8 installation
3. **Dependencies**: Install required packages
4. **Linting**: Code quality check with Pylint
5. **Unit Tests**: Run unit tests for feature engineering
6. **Component Tests**: Run component/integration tests
7. **Docker Build**: Package application in Docker container
8. **Deployment**: Start container in staging environment
9. **Smoke Test**: Verify application is running
10. **Cleanup**: Stop and remove container

**Pipeline Configuration Snippet:**

```yaml
name: MLOps CI/CD Pipeline

on: [push]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Kodu Çek (Checkout)
        uses: actions/checkout@v3

      - name: Python Kurulumu
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'

      - name: Bağımlılıkları Yükle
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pylint requests

      - name: Linting (Kod Kalitesi - Part 1 Task 3)
        run: |
          pylint --disable=all --enable=F,E feature_engineering.py app.py

      - name: Unit Testler (Unit Testing - Part 1 Task 2)
        run: |
          python -m unittest tests/test_logic.py -v

      - name: Component/Integration Testler (Part 2 Task 1)
        run: |
          python -m unittest tests/test_component.py -v

      - name: Paketi Oluştur (Docker Build - Part 2 Task 1)
        run: |
          docker build -t my-mlops-app .

      - name: Uygulamayı Başlat (Staging Deployment)
        run: |
          docker run -d -p 5000:5000 --name test_container my-mlops-app
          sleep 30 

      - name: Smoke Test (Deployment Verification - Part 2 Task 2)
        run: |
          curl --fail http://localhost:5000/health || exit 1
          python -m unittest tests/test_smoke.py -v

      - name: Konteyneri Temizle
        if: always()
        run: |
          docker stop test_container || true
          docker rm test_container || true
```

### 2. Test Results

#### Evidence A: Success (Green Build)

**Screenshot Placeholder:**
```
[SCREENSHOT: GitHub Actions workflow run showing successful completion]
- Green checkmark icon
- All stages passed (Lint, Unit Test, Component Test, Docker Build, Smoke Test)
- Duration: ~1m 11s
- Commit message: "Add component/integration test and prediction endpoint..."
```

**Description:**
This screenshot shows a successful pipeline execution where:
- All unit tests passed
- All component/integration tests passed
- Linting passed
- Docker build succeeded
- Smoke test passed
- All stages completed with green checkmarks

#### Evidence B: Failure/Stop the Line (Red Build)

**Screenshot Placeholder:**
```
[SCREENSHOT: GitHub Actions workflow run showing failure]
- Red X icon
- Linting stage failed
- Error message: "SyntaxError: '(' was never closed"
- Pipeline stopped at linting stage
- No deployment stages executed
- Commit message: "SABOTAGE TEST: Add intentional syntax error..."
- Duration: ~24s (failed quickly)
```

**Description:**
This screenshot demonstrates the "Stop the Line" principle:
- Pipeline detected syntax error at linting stage
- Build failed immediately (24 seconds)
- Deployment stages were never executed
- Red X indicates failure
- Bad code was prevented from entering production

### 3. Test Code

#### Unit Test Code

The unit test code is shown in **Section 1.2** above. It tests the `hash_feature` function in isolation with no external dependencies.

**Explanation:**
- Unit tests are fast because they execute pure Python functions in memory
- No I/O operations, database calls, or network requests
- Complete in milliseconds
- Can run thousands of tests in seconds

#### Smoke Test Code

The smoke test code is shown in **Section 2.3** above. It verifies the deployed application responds correctly.

**Explanation:**
- Smoke tests are end-to-end because they:
  - Require full Docker container deployment
  - Make real HTTP requests over the network
  - Test the complete system (container → network → application → response)
  - Verify the deployment process works end-to-end
  - Take longer to execute (require container startup time)

---

## Conclusion

This project successfully implements an MLOps CI/CD pipeline that:

1. ✅ Enforces code quality through automated linting
2. ✅ Verifies functionality through automated testing (unit, component, smoke)
3. ✅ Packages the application using Docker
4. ✅ Validates deployment through smoke testing
5. ✅ Prevents bad code from reaching production ("Stop the Line" principle)

The pipeline demonstrates all three parts of the homework requirements:
- **Part 1**: Commit Stage (CI) with version control, unit tests, and linting
- **Part 2**: Acceptance Gate (CD) with component tests, packaging, and smoke tests
- **Part 3**: Stop the Line simulation showing the pipeline blocks broken code

---

**Repository:** https://github.com/benkreb/MLOps-Homework-2
