# Repository Guidelines

## Project Structure & Module Organization

FinTrack is a Django 6 project. Project settings and root routing live in `core/`. Feature apps are under `apps/`: `account` handles authentication/profile/gamification, `tracker` handles budget records and dashboards, `dashboard` provides dashboard routing/views, and `AI` contains chatbot/advice models, services, and templates. Shared base templates are in `templates/`; app-specific templates live inside each app, for example `apps/tracker/templates/tracker/partials/`. Tests currently use both app-level `tests.py` files and the top-level `test_endpoints.py`.

## Build, Test, and Development Commands

Create and activate a virtual environment before installing dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the local server with `python manage.py runserver`. Apply database changes with `python manage.py migrate`; create migrations after model changes with `python manage.py makemigrations`. Run tests with `pytest`, which uses `core.settings` from `pytest.ini`.

## Coding Style & Naming Conventions

Use standard Python/Django style: 4-space indentation, snake_case for functions, variables, template names, and URL names, and PascalCase for models, forms, and class-based views. Keep business logic in app `services.py` where one already exists, views in `views.py`, forms in `forms.py`, and model changes in `models.py` plus migrations. Preserve the existing template organization and use partial templates for HTMX-updated fragments. Keep imports explicit and local to the app when possible.

## Testing Guidelines

Add focused pytest/Django tests for new views, services, models, and endpoint behavior. Name new test files `test_*.py` or place app tests in `tests.py`; name test functions `test_<expected_behavior>`. Prefer assertions on status codes, redirects, template usage, database side effects, and rendered context. Run `pytest` before submitting changes.

## Commit & Pull Request Guidelines

Recent commits use short, informal subjects such as `add` and `added`; keep future subjects concise but more descriptive, for example `Add budget limit validation`. Pull requests should include a short summary, test results, linked issues when applicable, and screenshots for UI/template changes. Call out migrations, `.env` changes, or any behavior that affects existing SQLite data.

## Security & Configuration Tips

Do not commit secrets or local environment files. `.env` is ignored and should contain values such as `GEMINI_API_KEY`. Avoid committing generated local artifacts such as `venv/`, `media/`, `staticfiles/`, logs, and local database changes unless explicitly required for the task.
