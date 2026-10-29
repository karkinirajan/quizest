# Versions

Resolved in `uv.lock` on 2026-10-29. "Previous" is the old `requirements.txt` (2022 pins).

| Component | Version | Previous | Note |
|---|---|---|---|
| Python | 3.13 | 3.10 | `requires-python >=3.13` |
| Django | 5.2.18 | 4.0.4 | 5.2 is the LTS line |
| django-allauth | 65.x | 0.50.0 | needs `AccountMiddleware`; legacy settings replaced by `ACCOUNT_LOGIN_METHODS` / `ACCOUNT_SIGNUP_FIELDS` |
| django-jazzmin | 3.0.5 | 2.5.0 | |
| django-crispy-forms | 2.7 | not pinned (missing) | + crispy-bootstrap5 for the Bootstrap 5 pack |
| Pillow | 13.0.0 | 9.2.0 | |
| WhiteNoise | 6.12.0 | 5.x (settings) | storage now via `STORAGES` |
| dj-database-url | 3.1.2 | 0.4.0 | |
| gunicorn | 26.2.0 | 20.1.0 | |
| psycopg | 3.3.6 (binary) | psycopg2 + psycopg2-binary | duplicate drivers replaced by one |

Removed: django-mptt (listed and installed but never used), cryptography/PyJWT/oauthlib/etc. pins (pulled in by allauth where needed), django-js-asset.

Dev: pytest, pytest-django, ruff.
