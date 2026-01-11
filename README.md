# MLOps Homework - CI/CD Pipeline Projesi

Bu proje, MLOps dersi için hazırlanmış bir CI/CD pipeline örneğidir.

## Proje Yapısı

```
mlops_homework/
├── app.py                    # Ana Flask uygulaması
├── feature_engineering.py    # Özellik mühendisliği fonksiyonları
├── requirements.txt          # Python bağımlılıkları
├── Dockerfile                # Docker konteyner yapılandırması
├── tests/
│   ├── test_logic.py        # Unit testler (hızlı, dış bağımlılık yok)
│   └── test_smoke.py        # Smoke testler (end-to-end, Docker gerekli)
└── .github/workflows/
    └── main.yml             # GitHub Actions CI/CD pipeline
```

## Pipeline Aşamaları

1. **Build**: Kod checkout ve Python kurulumu
2. **Unit Test**: Feature engineering fonksiyonlarının testi (hızlı)
3. **Lint**: Kod kalitesi kontrolü (pylint)
4. **Package**: Docker image oluşturma
5. **Smoke Test**: Uygulamanın çalışır durumda olduğunu doğrulama (end-to-end)

## Yerel Test

### Unit Testleri Çalıştırma

```bash
python -m unittest tests/test_logic.py -v
```

### Linting

```bash
pip install pylint
pylint feature_engineering.py app.py
```

### Docker ile Test

```bash
# Docker image oluştur
docker build -t my-mlops-app .

# Konteyneri çalıştır
docker run -d -p 5000:5000 --name test_container my-mlops-app

# Health check
curl http://localhost:5000/health

# Smoke test
python -m unittest tests/test_smoke.py -v

# Konteyneri durdur
docker stop test_container
docker rm test_container
```

## GitHub Actions

Pipeline otomatik olarak her `push` işleminde çalışır. Pipeline'ın başarısız olması durumunda (örneğin linting hatası veya test hatası), build durur ve "stop the line" prensibi uygulanır.

## Test Açıklamaları

- **Unit Testler**: Dış bağımlılık olmadan sadece fonksiyon mantığını test ettiği için hızlıdır.
- **Smoke Testler**: Docker konteyneri ayağa kaldırıp gerçek bir HTTP isteği attığı ve sistemin çalışır olduğunu doğruladığı için uçtan uca (end-to-end) bir testtir.

