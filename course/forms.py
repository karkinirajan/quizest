from allauth.account.forms import LoginForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from course.models import Profile, Store


class Loginform(LoginForm):
    def __init__(self, *args, **kwargs):
        super(Loginform, self).__init__(*args, **kwargs)

        self.fields["login"] = forms.CharField(
            max_length=100,
            label="Username",
            widget=forms.TextInput(
                attrs={
                    "placeholder": "johndoe",
                    "class": "form-control",
                    "id": "input-email",
                }
            ),
        )
        self.fields["password"] = forms.CharField(
            label="Password",
            widget=forms.PasswordInput(
                attrs={
                    "placeholder": "Password",
                    "class": "form-control",
                    "id": "input-password",
                }
            ),
        )


# creating a form
class StoreForm(forms.ModelForm):
    # create meta class
    class Meta:
        # specify model to be used
        model = Store

        # specify fields to be used
        fields = [
            "name",
            "uploaded_file",
        ]


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "image",
        ]
