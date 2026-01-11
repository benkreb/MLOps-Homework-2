# MLOps Homework - CI/CD Pipeline Project

This project is a CI/CD pipeline example prepared for the MLOps course.

## Project Structure

```
mlops_homework/
├── app.py                    # Main Flask application
├── feature_engineering.py    # Feature engineering functions
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker container configuration
├── tests/
│   ├── test_logic.py        # Unit tests (fast, no external dependencies)
│   ├── test_component.py    # Component/Integration tests
│   └── test_smoke.py        # Smoke tests (end-to-end, requires Docker)
└── .github/workflows/
    └── main.yml             # GitHub Actions CI/CD pipeline
```

## Pipeline Stages

1. **Build**: Code checkout and Python setup
2. **Lint**: Code quality check (pylint)
3. **Unit Test**: Feature engineering function tests (fast, isolated)
4. **Component/Integration Test**: Tests interaction between model serving logic and feature engineering
5. **Package**: Docker image build
6. **Smoke Test**: Verifies the application is up and running (end-to-end)

## Local Testing

### Run Unit Tests

```bash
python -m unittest tests/test_logic.py -v
```

### Run Component/Integration Tests

```bash
python -m unittest tests/test_component.py -v
```

### Linting

```bash
pip install pylint
pylint feature_engineering.py app.py
```

### Docker Testing

```bash
# Build Docker image
docker build -t my-mlops-app .

# Run container
docker run -d -p 5000:5000 --name test_container my-mlops-app

# Health check
curl http://localhost:5000/health

# Smoke test
python -m unittest tests/test_smoke.py -v

# Stop container
docker stop test_container
docker rm test_container
```

## GitHub Actions

The pipeline runs automatically on every `push` operation. If the pipeline fails (e.g., linting error or test failure), the build stops and the "stop the line" principle is applied.

## Test Explanations

- **Unit Tests**: Fast because they test only function logic without external dependencies (no database, network calls).
- **Component/Integration Tests**: Test the interaction between different components (e.g., model serving logic with feature engineering) to ensure proper integration.
- **Smoke Tests**: End-to-end tests because they spin up a Docker container, send a real HTTP request, and verify that the system is working correctly.
