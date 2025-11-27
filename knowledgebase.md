# Contrast2 Project Knowledgebase

This document provides a comprehensive overview of the Contrast2 Django project architecture, technology stack, and development practices.

## Technology Stack

### Core Framework
- **Python:** 3.11 (>3.10, <3.12)
- **Django:** 5.1.8
- **Django REST Framework:** 3.16.1
- **Dependency Management:** Poetry (pyproject.toml)

### Database
- **PostgreSQL:** 13-15
- **Connection:** postgresql://contrast_api_user:contrast_api_pass@127.0.0.1:5432/contrast_api_db

### Key Django Packages
- **django-configurations:** 2.5.1 (settings management)
- **django-filter:** 25.1
- **drf-spectacular:** 0.28.0 (OpenAPI/Swagger)
- **djangorestframework-simplejwt:** 5.4.0 (JWT auth)
- **django-import-export:** 4.3.13
- **django-cors-headers:** 4.9.0
- **django-two-factor-auth:** 1.18.1
- **django-simple-history:** 3.7.0
- **django-spa:** Custom fork for multi-SPA support

### Storage & Cloud
- **boto3:** 1.40.59+ (AWS S3)
- **django-storages:** 1.14.6
- **whitenoise:** 6.2.0 (static files)
- **Pillow:** 11.2.1 (images)

### Scientific Computing
- **numpy:** 2.2.4
- **pandas:** 2.2.3
- **matplotlib:** 3.10.3
- **nibabel:** 5.3.2 (neuroimaging)
- **nilearn:** 0.12.1 (neuroimaging)

### Development Tools
- **pytest:** 8.4.1
- **ruff:** 0.11.4 (linting, 120-char lines)
- **gunicorn:** 23.0.0 (production server)
- **sentry-sdk:** 2.38.0 (error tracking)

## Project Structure

```
Contrast2/
├── contrast_api/              # Main Django project
│   ├── settings.py           # Django configurations
│   ├── middleware.py         # Custom middleware
│   ├── application_services/ # Application services
│   ├── domain_services/      # Domain logic
│   └── technical_services/   # Technical utilities
│
├── studies/                  # ConTraSt app
│   ├── models/              # Study, Experiment, etc.
│   ├── views/               # API viewsets
│   ├── serializers.py       # DRF serializers
│   ├── processors/          # Graph processors
│   ├── parsers/             # Data parsing
│   └── tests/               # Test suite (22 files)
│
├── uncontrast_studies/      # UnConTraSt app
│   ├── models/              # Unconsciousness models
│   ├── views/               # API viewsets
│   ├── processors/          # Graph processors
│   └── tests/               # Test suite (18 files)
│
├── users/                   # User management
├── configuration/           # Global config
├── approval_process/        # Study approval
│
├── frontapp/                # Frontend builds
│   ├── contrast/
│   └── uncontrast/
│
├── deploy/
│   └── Dockerfile
├── .github/workflows/ci.yml
└── docker-compose.yml
```

## Django Configuration

### Configuration Classes (django-configurations)

1. **Base:** Default settings
2. **Development:** Debug mode, filesystem storage
3. **Testing:** Fast password hashing, test DB (port 5433)
4. **Staging:** S3 storage, restricted CORS
5. **Production:** Heroku, Sentry, S3

### Multi-SPA Architecture

- **ConTraSt:** contrastdb.tau.ac.il
- **UnConTraSt:** uncontrastdb.tau.ac.il, localhost:8000
- Custom `MultiSPAMiddleware` for routing

### Key Settings

- **Timezone:** Asia/Jerusalem (USER_TZ env var)
- **Page Size:** 30 items
- **JWT Lifetime:** 30 days
- **2FA Remember:** 600 seconds

## API Structure

### Authentication
- `POST /api/api-token-auth/` - JWT token
- `POST /api/api-token-refresh/` - Refresh

### Studies API (/api/studies/)
- `/studies/` - Approved studies
- `/excluded_studies/` - Excluded studies
- `/experiments_graphs/` - Graph data
- `/submitted_studies/` - Submission workflow
- Nested routes for experiments and relations

### UnContrast API (/api/uncontrast_studies/)
- Similar structure to studies
- Additional: suppressed_stimuli, target_stimuli, findings

### Documentation
- `/api/schema/` - OpenAPI schema
- `/api/schema/swagger-ui/` - Swagger (dev)
- `/api/schema/redoc/` - ReDoc (dev)

## Domain Models

### ConTraSt (studies app)
- **Study** - Research study with DOI, approval
- **Experiment** - Experiments within studies
- **Author** - Study authors
- **Stimulus** - With modality, category, sub-category
- **Technique** - Brain imaging techniques
- **Paradigm** - Hierarchical paradigms
- **Task/Measure** - With types
- **ConsciousnessMeasure** - Consciousness measurement
- **Sample** - Study sample info
- **FindingTag** - With family and type
- **Interpretation** - Theory interpretations
- **Theory** - Hierarchical theory framework

### UnConTraSt (uncontrast_studies app)
- **UnConExperiment**
- **UnConConsciousnessMeasure**
- **UnConSuppressedStimulus/UnConTargetStimulus**
- **UnConParadigm** - Main and Specific
- **UnConProcessingDomain/UnConSuppressionMethod**
- **UnConTask/UnConSample**
- **UnConFinding/UnConOutcome**

## Testing

### Framework
- **pytest:** 8.4.1
- **Test Database:** PostgreSQL port 5433
- **Configuration:** DJANGO_CONFIGURATION=Testing

### Test Coverage
- studies/tests/ - 22 files
- uncontrast_studies/tests/ - 18 files
- Includes: endpoints, admin, graphs, services

### Running Tests
```bash
DJANGO_CONFIGURATION=Testing python manage.py test
```

## CI/CD Pipeline

### GitHub Actions (.github/workflows/ci.yml)

**Triggers:** Push, pull requests

**Jobs:**

1. **Security:** DevSkim scanning
2. **Test:**
   - Ubuntu + Python 3.11
   - PostgreSQL 15 service
   - Poetry install
   - Run tests with -v 3
3. **Deploy:**
   - Main branch only
   - Checkout ContrastFront repo
   - Build React apps (npm run build:contrast, build:uncontrast)
   - Deploy to Heroku (contrast2-api)

## Deployment

### Docker
- **Base:** python:3.11-slim-bookworm
- **Container:** Multi-stage build with Poetry
- **Services:** nginx, db (postgres:13), web

### Heroku
- **App:** contrast2-api
- **Procfile:** Runs migrations, gunicorn
- **Release:** load_atlas_data command
- **Storage:** S3 via Bucketeer
- **Monitoring:** Sentry (20% trace sample)

### Docker Compose (Local Dev)
```bash
docker-compose up
# Admin: admin/admin
# Port: 8080 (nginx), 8000 (web)
```

## Data Management

### Management Commands

1. **load_historic_data.py** - Load ConTraSt studies from Excel
2. **load_atlas_data.py** - Load AAL brain atlas
3. **load_uncon_data.py** - Load UnConTraSt studies

### Data Processing

- **Parsers:** process_row.py, parsing_findings_Contrast2.py
- **Processors:** Graph data generation (pie, bar, trends)
- **Import/Export:** django-import-export resources

## Development Practices

### Code Quality
- **Linting:** ruff (120-char lines)
- **Commands:**
  ```bash
  ruff check . --fix
  ruff format
  ```

### Architecture
- Service layer separation (application/domain/technical)
- ViewSet-based API design
- Custom managers and querysets
- Middleware for cross-cutting concerns

### Monitoring
- Sentry for errors
- QueryCount for performance
- Request logging

## External Services

- **Email:** Mailgun (EU)
- **Storage:** AWS S3
- **Error Tracking:** Sentry.io
- **Frontend:** Separate repo (Mudrik-Lab/ContrastFront)

## License

- **Code:** GNU GPLv3
- **Data:** CC-BY-SA-4.0
- **Contact:** MudrikLab@tauex.tau.ac.il
