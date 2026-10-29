from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "course"

    def ready(self):
        import course.signals  # noqa: F401  (registers the profile post_save handlers)
