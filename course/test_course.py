import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from course.models import Profile, Store


@pytest.fixture
def user(db):
    return User.objects.create_user("ann", "ann@example.com", "pw-12345-xyz")


@pytest.fixture
def logged_in(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def store(db):
    return Store.objects.create(
        name="Course A", uploaded_file=SimpleUploadedFile("a.zip", b"PK-data")
    )


def upload(name="b.zip", data=b"PK\x03\x04zip-bytes"):
    return SimpleUploadedFile(name, data)


# --- access control -------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["dashboard", "create", "profile"])
def test_pages_require_login(client, db, name):
    res = client.get(reverse(name))
    assert res.status_code == 302 and "login" in res.url


@pytest.mark.parametrize("name", ["store-update", "store-delete"])
def test_store_pages_require_login(client, store, name):
    assert client.get(reverse(name, args=[store.id])).status_code == 302


# --- stores ---------------------------------------------------------------------------------


def test_dashboard_lists_recent_stores_and_users(logged_in, store):
    res = logged_in.get(reverse("dashboard"))
    assert res.status_code == 200
    assert list(res.context["stores"]) == [store]
    assert res.context["users"].count() == 1


def test_create_renders_and_saves_with_the_uploaded_file(logged_in):
    assert logged_in.get(reverse("create")).status_code == 200
    res = logged_in.post(reverse("create"), {"name": "New course", "uploaded_file": upload()})
    assert res.status_code == 302 and res.url == reverse("dashboard")
    saved = Store.objects.get(name="New course")
    assert saved.uploaded_file.read() == b"PK\x03\x04zip-bytes"


def test_create_without_a_file_shows_errors(logged_in):
    res = logged_in.post(reverse("create"), {"name": "No file"})
    assert res.status_code == 200 and "uploaded_file" in res.context["form"].errors
    assert Store.objects.count() == 0


def test_update_changes_the_name_and_can_replace_the_file(logged_in, store):
    url = reverse("store-update", args=[store.id])
    assert logged_in.get(url).status_code == 200
    res = logged_in.post(url, {"name": "Renamed", "uploaded_file": upload("new.zip", b"PKnew")})
    assert res.status_code == 302
    store.refresh_from_db()
    assert store.name == "Renamed" and store.uploaded_file.read() == b"PKnew"


def test_update_keeps_the_existing_file_when_none_is_sent(logged_in, store):
    old = store.uploaded_file.name
    logged_in.post(reverse("store-update", args=[store.id]), {"name": "Only name"})
    store.refresh_from_db()
    assert store.name == "Only name" and store.uploaded_file.name == old


def test_delete_needs_a_post(logged_in, store):
    url = reverse("store-delete", args=[store.id])
    assert logged_in.get(url).status_code == 200  # confirmation page
    assert Store.objects.count() == 1
    assert logged_in.post(url).status_code == 302
    assert Store.objects.count() == 0


def test_unknown_store_ids_are_404(logged_in, db):
    assert logged_in.get(reverse("store-update", args=[999])).status_code == 404
    assert logged_in.post(reverse("store-delete", args=[999])).status_code == 404


# --- accounts and profiles ------------------------------------------------------------------


def test_profile_is_created_with_the_user(user):
    assert Profile.objects.filter(user=user).exists()
    assert str(user.profile) == "ann Profile"


def test_profile_save_does_not_crash_without_the_default_image_file(user):
    user.profile.full_name = "Ann Lee"
    user.profile.save()  # default.jpg is not on disk under the temp MEDIA_ROOT
    user.profile.refresh_from_db()
    assert user.profile.full_name == "Ann Lee"


def test_register_creates_the_user_and_stores_the_full_name(client, db):
    res = client.post(
        reverse("register"),
        {
            "username": "bob",
            "email": "bob@example.com",
            "full_name": "Bob Stone",
            "password1": "Str0ng-pass-phrase!",
            "password2": "Str0ng-pass-phrase!",
        },
    )
    assert res.status_code == 302
    bob = User.objects.get(username="bob")
    assert bob.profile.full_name == "Bob Stone" and bob.profile.email == "bob@example.com"


def test_register_rejects_mismatched_passwords(client, db):
    res = client.post(
        reverse("register"),
        {
            "username": "bob",
            "email": "b@example.com",
            "full_name": "B",
            "password1": "Str0ng-pass-phrase!",
            "password2": "different",
        },
    )
    assert res.status_code == 200 and not User.objects.filter(username="bob").exists()


def test_profile_update_saves_both_forms(logged_in, user):
    res = logged_in.post(
        reverse("profile"),
        {"username": "ann2", "email": "new@example.com", "full_name": "Ann New"},
    )
    assert res.status_code == 302
    user.refresh_from_db()
    assert user.username == "ann2" and user.profile.full_name == "Ann New"


def test_profile_update_with_invalid_data_does_not_save_or_claim_success(logged_in, user):
    res = logged_in.post(reverse("profile"), {"username": "", "email": "not-an-email"})
    assert res.status_code == 200  # form re-rendered with errors
    user.refresh_from_db()
    assert user.username == "ann"


def test_login_pages_render(client, db):
    assert client.get(reverse("login")).status_code == 200
    assert client.get(reverse("account_login")).status_code == 200


def test_login_with_username_works(client, user):
    assert client.login(username="ann", password="pw-12345-xyz")


def test_admin_renders_with_the_jazzmin_theme(client, db):
    admin = User.objects.create_superuser("root", "root@example.com", "pw-12345-xyz")
    client.force_login(admin)
    assert client.get("/admin/").status_code == 200
    assert client.get("/admin/course/store/").status_code == 200


# --- upload validation (security) ------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    [
        "page.html",
        "image.svg",
        "run.js",
        "shell.php",
        "tool.exe",
        "x.sh",
        "noextension",
        "a.zip.html",
    ],
)
def test_dangerous_or_unknown_extensions_are_rejected(logged_in, name):
    res = logged_in.post(
        reverse("create"), {"name": "bad", "uploaded_file": upload(name, b"<script>")}
    )
    assert res.status_code == 200 and "uploaded_file" in res.context["form"].errors
    assert Store.objects.count() == 0


@pytest.mark.parametrize("name", ["a.zip", "b.pdf", "c.pptx", "d.docx", "e.csv", "UPPER.ZIP"])
def test_allowed_extensions_with_matching_content_are_accepted(logged_in, name):
    body = (
        b"%PDF-1.4 ..."
        if name.endswith("pdf")
        else b"PK\x03\x04..."
        if name.lower().endswith(("zip", "pptx", "docx"))
        else b"a,b\n1,2\n"
    )
    res = logged_in.post(reverse("create"), {"name": "ok", "uploaded_file": upload(name, body)})
    assert res.status_code == 302 and Store.objects.count() == 1


def test_content_must_match_the_extension(logged_in):
    for name, body in (("fake.zip", b"<html>not a zip"), ("fake.pdf", b"MZ\x90\x00 exe")):
        res = logged_in.post(
            reverse("create"), {"name": "bad", "uploaded_file": upload(name, body)}
        )
        assert res.status_code == 200
        assert "does not match" in str(res.context["form"].errors["uploaded_file"])
    assert Store.objects.count() == 0


def test_oversized_files_are_rejected(logged_in, settings):
    settings.STORE_MAX_UPLOAD_MB = 1
    big = upload("big.zip", b"PK" + b"0" * (1024 * 1024))
    res = logged_in.post(reverse("create"), {"name": "big", "uploaded_file": big})
    assert res.status_code == 200 and "limit" in str(res.context["form"].errors["uploaded_file"])


def test_the_allow_list_is_configurable(logged_in, settings):
    settings.STORE_ALLOWED_EXTENSIONS = ["csv"]
    zipped = logged_in.post(
        reverse("create"), {"name": "z", "uploaded_file": upload("a.zip", b"PK..")}
    )
    assert zipped.status_code == 200
    ok = logged_in.post(reverse("create"), {"name": "c", "uploaded_file": upload("a.csv", b"a,b")})
    assert ok.status_code == 302


def test_replacing_a_file_in_update_is_validated_too(logged_in, store):
    url = reverse("store-update", args=[store.id])
    res = logged_in.post(url, {"name": "x", "uploaded_file": upload("evil.html", b"<script>")})
    assert res.status_code == 200
    store.refresh_from_db()
    assert store.uploaded_file.name.endswith(".zip")


def test_the_admin_form_enforces_the_same_rules(db):
    from django.core.exceptions import ValidationError

    from course.validators import validate_upload

    with pytest.raises(ValidationError):
        validate_upload(SimpleUploadedFile("x.svg", b"<svg onload=alert(1)>"))
