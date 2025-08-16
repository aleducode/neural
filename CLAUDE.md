# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Local Development with Docker
- **Start development environment**: `docker-compose -f local.yml up`
- **Build and start**: `docker-compose -f local.yml up --build`
- **Django shell**: `docker-compose -f local.yml exec django python manage.py shell`
- **Create superuser**: `docker-compose -f local.yml exec django python manage.py createsuperuser`
- **Run migrations**: `docker-compose -f local.yml exec django python manage.py migrate`
- **Make migrations**: `docker-compose -f local.yml exec django python manage.py makemigrations`

### Direct Django Commands (without Docker)
- **Run development server**: `python manage.py runserver`
- **Run tests**: `pytest`
- **Test with coverage**: `coverage run -m pytest && coverage html`
- **Type checking**: `mypy neural`
- **Create superuser**: `python manage.py createsuperuser`
- **Database migrations**: `python manage.py migrate`
- **Make migrations**: `python manage.py makemigrations`

### Celery (Background Tasks)
- **Start celery worker**: `celery -A config.celery_app worker -l info`
- **Start celery beat**: `celery -A config.celery_app beat -l info`

### Production Deployment
- **Production environment**: `docker-compose -f production.yml up`

## Project Architecture

### Technology Stack
- **Framework**: Django 4.2
- **Database**: PostgreSQL
- **Cache/Message Broker**: Redis
- **Background Tasks**: Celery with Flower monitoring
- **Frontend**: Bootstrap-based templates with custom CSS/JS
- **Containerization**: Docker with separate local/production configurations
- **Reverse Proxy**: Traefik (production)

### Application Structure
```
neural/
├── config/                 # Django project configuration
│   ├── settings/          # Environment-specific settings
│   │   ├── base.py       # Base settings
│   │   ├── local.py      # Development settings
│   │   ├── production.py # Production settings
│   │   └── test.py       # Test settings
│   ├── urls.py           # Root URL configuration
│   └── celery_app.py     # Celery configuration
├── neural/               # Main application package
│   ├── users/           # User management app
│   ├── training/        # Training/gym management app
│   ├── templates/       # Django templates
│   ├── static/         # Static files (CSS, JS, images)
│   └── utils/          # Shared utilities
└── compose/            # Docker configurations
```

### Core Applications

#### Users App (`neural/users/`)
- Custom User model extending AbstractUser with email as username
- User authentication and profile management
- Membership and payment tracking models
- User rankings and statistics

#### Training App (`neural/training/`)
- Training session management
- Class scheduling and booking system
- Space and training type management
- User training history and statistics

### Key Models
- **User**: Custom user model with phone, photo, membership data
- **TrainingType**: Different types of training (group/individual)
- **Space**: Physical training spaces
- **UserTraining**: Training session bookings
- **Classes**: Scheduled training classes
- **Slot**: Available time slots for training

### Development Patterns
- Uses Django's app structure with clear separation of concerns
- Custom base model `NeuralBaseModel` for common fields
- Slug generation for SEO-friendly URLs
- Celery tasks for background processing
- Django REST Framework for API endpoints
- Template inheritance with base templates

### Configuration Notes
- Settings split by environment (local/production/test)
- Environment variables managed via django-environ
- Database configured via DATABASE_URL
- Static files served via WhiteNoise in production
- Time zone set to "America/Bogota"
- Language set to "es-CO" (Spanish Colombia)

### Testing
- Uses pytest with Django settings
- Coverage configuration excludes migrations and tests
- MyPy type checking configured for Django
- Test database reuse enabled for faster testing

### Code Quality
- Flake8 linting with 300 character line limit
- MyPy type checking enabled
- Black code formatting (referenced in README)
- Git hooks excluded migrations and static cache from linting