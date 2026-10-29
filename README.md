# Quizest

A Django app for uploading and managing course/quiz packages. Signed-in users upload a file (for example an exported course package), list, replace and delete uploads from a dashboard, and manage their profile. Accounts support username/email login and optional Google sign-in (django-allauth); the admin uses the Jazzmin theme.

## Features

- Dashboard with the latest uploads and newest users.
- Create, update (including replacing the file) and delete uploads; deleting asks for confirmation and requires a POST.
- Registration (with full name), login/logout, password reset, and a profile page with an avatar.
- Google sign-in when `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set.
- Uploads are validated: extension allow-list (default `zip`, `pdf`, `pptx`, `docx`, `xlsx`, `csv`, `txt`; HTML, SVG, JavaScript, PHP and executables are refused), a size cap (default 200 MB) and a check that ZIP/Office/PDF files really start with the right signature. Configure with `STORE_ALLOWED_EXTENSIONS` and `STORE_MAX_UPLOAD_MB`.
- Static course assets are served from `static/` (an exported course player); `staticfiles/` is generated and git-ignored.

## Stack

Python 3.13, Django 5.2 LTS, django-allauth 65, django-jazzmin, django-crispy-forms (Bootstrap 5), Pillow, WhiteNoise, gunicorn; SQLite by default or PostgreSQL via `DATABASE_URL`. Versions: [VERSIONS.md](./VERSIONS.md).

## Quickstart

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/kneeraazon404/quizest.git
cd quizest
export DJANGO_DEBUG=true      # local work only; a dev secret key is used
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | required unless `DJANGO_DEBUG=true` | startup fails without it in production |
| `DJANGO_DEBUG` | `false` | debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | comma-separated hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | comma-separated origins |
| `DATABASE_URL` | local SQLite file | any dj-database-url URL |
| `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | unset | enable Google sign-in |
| `STORE_ALLOWED_EXTENSIONS` | `zip,pdf,pptx,docx,xlsx,csv,txt` | comma-separated upload allow-list |
| `STORE_MAX_UPLOAD_MB` | `200` | maximum upload size |

With `DJANGO_DEBUG=false` the app also enables HTTPS redirect, secure cookies and HSTS. `Procfile` runs gunicorn; run `migrate` and `collectstatic --noinput` on deploy.

## Testing

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
```

40 tests cover access control, upload create/update/delete (with real file uploads), upload validation, registration, profiles and the admin. They use `courseapp.settings_test` (in-memory SQLite, temporary media). CI: `.github/workflows/ci.yml`.

## Serving uploads safely

The app stores uploads under `MEDIA_ROOT` but does not serve them in production (Django serves `/media/` only when `DJANGO_DEBUG=true`). Serve them from your web server or object storage on a separate origin, with `Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`, so an uploaded file can never run as a page on your site's origin.

## Project structure

```
courseapp/   settings, urls, wsgi/asgi, settings_test.py
course/      models (Profile, Store), views, forms, allauth adapter, templates, tests
static/      exported course assets and player files
```

## License

No license file is present in this repository.
