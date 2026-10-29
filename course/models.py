import os

from django.contrib.auth.models import User
from django.db import models
from PIL import Image

from course.validators import validate_upload


class Profile(models.Model):
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # default.jpg may not exist on disk (fresh checkout/tests); skip resizing then.
        if not self.image or not os.path.exists(self.image.path):
            return

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Store(models.Model):
    name = models.CharField(max_length=100)
    uploaded_file = models.FileField(upload_to="uploads/", validators=[validate_upload])
    converted_file = models.FileField(
        upload_to="converted_files", null=True, blank=True, validators=[validate_upload]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
