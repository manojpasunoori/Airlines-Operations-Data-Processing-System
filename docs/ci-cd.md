# CI/CD Pipeline

GitHub Actions now performs:

- Java service build + tests (Maven)
- Python service dependency + import smoke tests
- React dashboard build
- Docker image build per component
- Trivy vulnerability scanning
- GHCR push on main branch

Workflow file: `.github/workflows/ci.yml`
