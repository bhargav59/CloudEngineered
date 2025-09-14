# CloudEngineered Platform
CloudEngineered is a Django-based platform for cloud engineering tool reviews with AI-powered content generation. The platform targets cloud engineers, DevOps professionals, and technical decision-makers.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Working Effectively

### Bootstrap and Dependencies
- Create virtual environment: `python3 -m venv venv` -- takes 3 seconds
- Activate environment: `source venv/bin/activate`
- Upgrade pip: `pip install --upgrade pip` -- takes 2 seconds
- Install dependencies: `pip install -r requirements/development.txt` -- **NEVER CANCEL: Can take 5-15 minutes due to large dependency set (AI libraries, web scraping, etc.). Set timeout to 20+ minutes.**
  - **KNOWN ISSUE**: PyPI timeout errors may occur. If this happens, try:
    - `pip install --timeout 300 -r requirements/development.txt`
    - Or install core dependencies first: `pip install Django psycopg2-binary redis celery djangorestframework`
    - Then install remaining dependencies in chunks
- **CRITICAL FIX**: The `django-sitemap` package in requirements/base.txt does not exist on PyPI. Remove this line or replace with Django's built-in sitemap framework before installing.

### Database Setup
- **IMPORTANT**: Ensure PostgreSQL is running: `sudo systemctl start postgresql`
- Create database: `createdb cloudengineered` (or `sudo -u postgres createdb cloudengineered`)
- Copy environment file: `cp .env.example .env`
- **MUST EDIT**: Update .env with correct database credentials, especially `DB_PASSWORD`
- Run migrations: `python manage.py migrate` -- takes 10-30 seconds
- Initialize platform: `python manage.py init_platform` -- takes 5-10 seconds
- Create superuser: `python manage.py createsuperuser`

### Redis Setup
- **IMPORTANT**: Ensure Redis is running: `sudo systemctl start redis-server`
- Test connection: `redis-cli ping` (should return "PONG")
- Default Redis URL: `redis://localhost:6379/1`

### Running the Application
- **Development server**: `python manage.py runserver` -- starts immediately, serves on http://localhost:8000
- **Celery worker** (separate terminal): `celery -A config worker -l info` -- **NEVER CANCEL: Starts in 10-15 seconds, runs indefinitely**
- **Celery beat scheduler** (separate terminal): `celery -A config beat -l info` -- **NEVER CANCEL: Starts in 5-10 seconds, runs indefinitely**
- **Static files**: `python manage.py collectstatic --noinput` -- takes 2-5 seconds

### Docker Alternative (Recommended for reliability)
- **IMPORTANT**: Stop system PostgreSQL/Redis first: `sudo systemctl stop postgresql redis-server`
- Build and start services: `cd docker && docker compose up --build` -- **NEVER CANCEL: Takes 5-15 minutes for first build. Set timeout to 20+ minutes.**
- Start just database services: `docker compose up -d db redis` -- takes 1-3 minutes
- Access containers: `docker compose exec web python manage.py shell`

## Testing and Quality Assurance

### Running Tests
- **All tests**: `python manage.py test` -- **NEVER CANCEL: Takes 2-5 minutes depending on test suite size. Set timeout to 10+ minutes.**
- **Specific app tests**: `python manage.py test apps.tools` -- takes 30-60 seconds
- **Test with coverage**: `coverage run --source='.' manage.py test && coverage report` -- takes 3-6 minutes
- **Settings for tests**: Uses `config.settings.testing` (SQLite in-memory, disabled migrations)

### Code Quality
- **Format code**: `black .` -- takes 5-10 seconds
- **Lint code**: `flake8 .` -- takes 5-10 seconds
- **Import sorting**: `isort .` -- takes 2-5 seconds
- **Type checking**: `mypy .` -- takes 10-30 seconds

### **CRITICAL**: Always run linting before committing or CI will fail:
```bash
black . && flake8 . && isort .
```

## Validation Scenarios

**ALWAYS test these scenarios after making changes:**

### 1. Basic Application Functionality
1. Start development server: `python manage.py runserver`
2. Access admin panel: http://localhost:8000/admin
3. Login with superuser credentials
4. Navigate to main site: http://localhost:8000
5. Verify site loads without errors

### 2. Database Operations
1. Create a new tool entry via admin
2. Test tool creation API endpoint
3. Verify data persistence across server restarts

### 3. Celery Task Processing
1. Start Celery worker in separate terminal
2. Trigger background task (e.g., AI content generation)
3. Monitor Celery logs for successful execution
4. Verify task results in database

### 4. AI Content Generation (if API keys available)
1. Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY in .env
2. Run: `python manage.py shell`
3. Test AI service: `from apps.ai.services import AIContentGenerator; generator = AIContentGenerator(); generator.test_connection()`

## Timing Expectations

**NEVER CANCEL these operations - they may take significant time:**

- **Virtual environment creation**: 3 seconds
- **Pip dependency installation**: 5-15 minutes (can timeout, retry if needed)
- **Docker build (first time)**: 5-15 minutes
- **Database migrations**: 10-30 seconds
- **Test suite execution**: 2-5 minutes
- **Static file collection**: 2-5 seconds
- **Celery worker startup**: 10-15 seconds

## Key Project Structure

```
cloudengineered/
├── apps/                    # Django applications
│   ├── ai/                 # AI content generation services
│   ├── tools/              # Tool models and management
│   ├── content/            # Articles and content management
│   ├── users/              # User management and profiles
│   ├── core/               # Base models and utilities
│   ├── analytics/          # Analytics and tracking
│   ├── automation/         # Background task automation
│   ├── affiliates/         # Affiliate link management
│   └── api/                # REST API endpoints
├── config/                 # Django configuration
│   ├── settings/           # Environment-specific settings
│   ├── celery.py          # Celery configuration
│   └── urls.py            # Main URL patterns
├── requirements/           # Dependencies by environment
├── docker/                # Docker configuration
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
└── manage.py             # Django management script
```

## Common Issues and Workarounds

### 1. Dependency Installation Failures
- **Symptom**: `pip install` timeouts or HTTP errors
- **Solution**: Use longer timeout: `pip install --timeout 300 -r requirements/development.txt`
- **Alternative**: Install core packages first, then AI packages separately

### 2. Database Connection Errors
- **Symptom**: "could not connect to server" errors
- **Solution**: Ensure PostgreSQL is running: `sudo systemctl start postgresql`
- **Alternative**: Use SQLite for development: Set `USE_SQLITE=True` in .env

### 3. Redis Connection Errors
- **Symptom**: "Connection refused" errors
- **Solution**: Start Redis: `sudo systemctl start redis-server`
- **Test**: `redis-cli ping` should return "PONG"

### 4. Port Conflicts in Docker
- **Symptom**: "port already in use" errors
- **Solution**: Stop system services: `sudo systemctl stop postgresql redis-server`
- **Alternative**: Modify docker-compose.yml port mappings

### 5. Missing django-sitemap Package
- **Symptom**: "No matching distribution found for django-sitemap"
- **Solution**: Remove `django-sitemap>=2.2.0` line from requirements/base.txt

### 6. Static Files Not Loading
- **Symptom**: CSS/JS files return 404
- **Solution**: Run `python manage.py collectstatic --noinput`

## Management Commands

### Platform Initialization
- `python manage.py init_platform` -- Initialize platform with sample data
- `python manage.py populate_search_data` -- Populate search indices
- `python manage.py createsuperuser` -- Create admin user

### Testing Commands  
- `python manage.py test_ai_generation` -- Test AI content generation
- `python manage.py test_tools_ai_integration` -- Test tools AI integration

### Development Utilities
- `python manage.py shell` -- Access Django shell
- `python manage.py dbshell` -- Access database shell
- `python manage.py check` -- Check for configuration issues

## API Access

- **Main site**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin
- **API root**: http://localhost:8000/api/
- **API documentation**: http://localhost:8000/api/docs/ (development only)

## Environment Variables

### Required
- `SECRET_KEY` -- Django secret key (auto-generated by setup)
- `DB_NAME` -- Database name (default: cloudengineered)
- `DB_USER` -- Database user (default: postgres)  
- `DB_PASSWORD` -- Database password (must set)

### Optional but Recommended
- `OPENAI_API_KEY` -- For AI content generation
- `ANTHROPIC_API_KEY` -- Alternative AI provider
- `GITHUB_TOKEN` -- For GitHub tool discovery
- `REDIS_URL` -- Redis connection (default: redis://localhost:6379/1)

### Development
- `DEBUG=True` -- Enable debug mode
- `USE_SQLITE=True` -- Use SQLite instead of PostgreSQL
- `CELERY_ALWAYS_EAGER=True` -- Run tasks synchronously

## Performance Notes

- **First startup**: Allow 15-30 seconds for full initialization
- **Cold Docker build**: 5-15 minutes for complete environment
- **Warm restarts**: 2-5 seconds for most operations
- **Database queries**: Optimized with select_related/prefetch_related
- **Caching**: Redis-based caching for API responses and templates

## Do Not Skip These Steps

1. **ALWAYS** run database migrations before starting the server
2. **ALWAYS** start Redis and PostgreSQL before Django
3. **ALWAYS** run Celery workers for background task processing
4. **ALWAYS** run code quality checks before committing changes
5. **ALWAYS** test the complete user flow after making changes
6. **NEVER** commit without testing database operations
7. **NEVER** deploy without running the full test suite

## Quick Validation Checklist

After any changes, **ALWAYS** verify:
- [ ] Database migrations apply cleanly: `python manage.py migrate`
- [ ] All tests pass: `python manage.py test` (wait for completion)
- [ ] Code quality checks pass: `black . && flake8 . && isort .`
- [ ] Server starts without errors: `python manage.py runserver`
- [ ] Admin panel is accessible: http://localhost:8000/admin
- [ ] Main site loads: http://localhost:8000
- [ ] Celery workers can be started: `celery -A config worker -l info`
- [ ] Basic tool creation works via admin interface

**Remember**: This platform includes AI features, complex background processing, and multiple data sources. Always allow sufficient time for operations to complete and test thoroughly in a realistic environment.