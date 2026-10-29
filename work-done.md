# Work done: quizest

Branch: `chore/modernize` (local, not pushed). Date: 2026-10-29. The repo had no uncommitted work.

## What was there
A Django 4.0 app (`course`, project `courseapp`) with 2022 pins, hardcoded secret key and `DEBUG = True` with `ALLOWED_HOSTS = ["*"]`, dummy Google credentials (`"123"`/`"456"`), an empty `tests.py`, and 10,344 tracked files: about 6,860 collected `staticfiles/`, 3,386 files in `static/` (exported course assets), `.DS_Store` files.

## Changes by file
| File | Before | Change |
|---|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | absent | New uv project, Python 3.13, Django 5.2 LTS |
| `requirements.txt`, `runtime.txt`, `Procfile` | 30 pins incl. unused mptt and two Postgres drivers; Procfile `gunicorn courseapp.wsgi` | Exported from lockfile; python-3.13; gunicorn `courseapp.wsgi:application` |
| `courseapp/settings.py` | hardcoded secret, DEBUG, wildcard hosts, dummy Google app, `STATICFILES_STORAGE`, `USE_L10N`, duplicate `MEDIA_ROOT`, commented-out database credentials | Env-driven (fails fast without a secret outside debug); Google app only from real env credentials; `STORAGES`; `DATABASE_URL`; allauth 65 settings and `AccountMiddleware`; crispy Bootstrap 5 pack; HTTPS/HSTS when not debug |
| `courseapp/settings_test.py` | absent | New |
| `course/views.py` | `profile` used `u_form.is_valid` without parentheses (always true) and always claimed "account created"; `update_view` ignored `request.FILES` so a file could not be replaced; convoluted create flow; register discarded the entered full name | Rewritten with the same URLs, names and templates: valid forms only, correct messages, files handled, full name and email stored on the profile |
| `course/models.py` | `Profile.save()` crashed if the image file was missing | Skips resizing when the file is absent |
| `course/forms.py` | imports in the middle of the file | Hoisted |
| `course/apps.py` | imports signals in `ready()` | Kept with a noqa (ruff's autofix removes it) |
| `course/tests.py` | empty | Deleted; `course/test_course.py` has 21 tests |
| `.github/workflows/ci.yml`, `.env.example` | absent | New |
| `.gitignore` | had basics | Also `staticfiles/`, `media/`, `db.sqlite3`, `.DS_Store`, caches |
| `staticfiles/` (6,860 files), `.DS_Store`, `.pyc` | tracked | Untracked with `git rm --cached`; `static/` (source course assets) stays |
| `README.md`, `VERSIONS.md`, `work-done.md` | generic README; absent | Rewritten from the code; new |

## A mistake I made and caught
I first removed `django-crispy-forms` as "unused" after a `grep` that had silently failed on a shell glob; the test run then failed with `'crispy_forms_tags' is not a registered tag library`. It is used by seven templates and is restored (with the Bootstrap 5 template pack, matching the site's Bootstrap 5.2 CSS). `django-mptt` was re-checked with a plain recursive grep and really is unused.

## Follow-up: automated security review (fixed)
A review of the commit flagged unrestricted file upload on `Store.uploaded_file`. Added `course/validators.py` (applied to both file fields, so the admin is covered; migration `0003_upload_validators`): an extension allow-list (configurable, HTML/SVG/JS/PHP/executables excluded by default), a size cap, and a signature check that ZIP/Office/PDF files start with the expected bytes. Tests cover dangerous extensions (including `a.zip.html`), mismatched content, oversize files, the configurable list, and replacing a file on update. The allow-list is a judgement call because the app never documented the expected types, so adjust `STORE_ALLOWED_EXTENSIONS` to what you really upload. The signature check proves the header, not that the whole file is safe; serving uploads from a separate origin as attachments (see README) remains the real protection.

## Verification (actual runs)
- `uv run pytest -q`: 40 passed. `uv run ruff check .` and `ruff format --check .`: clean.
- `makemigrations --check`: no changes. `collectstatic` under the production storage succeeded. `check --deploy`: only the two optional HSTS warnings.
- Not run: PostgreSQL, a browser, a real Google OAuth round trip.

## Needs your attention
- Any signed-in user can update or delete any upload (the model has no owner); that is how the app was designed, and I did not change it.
- The old secret key is in git history; rotate it.
- `static/` contains a large exported course player (3,386 files, possibly third-party licensed content).
- No license file exists.
- Nothing pushed. To publish: `git push -u origin chore/modernize`
