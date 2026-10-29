from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from course.forms import ProfileUpdateForm, StoreForm, UserRegisterForm, UserUpdateForm
from course.models import Store


@login_required
def dashboard(request):
    users = User.objects.all().order_by("-date_joined")[:3]
    stores = Store.objects.all().order_by("-created_at")[:3]
    return render(request, "dashboard.html", {"users": users, "stores": stores})


@login_required
def create_view(request):
    form = StoreForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("dashboard")
    return render(request, "store_form.html", {"form": form})


@login_required
def update_view(request, id):
    obj = get_object_or_404(Store, id=id)
    # request.FILES is needed so a replacement file can be uploaded
    form = StoreForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("/")
    return render(request, "update_view.html", {"form": form})


@login_required
def delete_view(request, id):
    obj = get_object_or_404(Store, id=id)
    if request.method == "POST":
        obj.delete()
        return redirect("/")
    return render(request, "delete_view.html", {})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.full_name = form.cleaned_data["full_name"]
            user.profile.email = user.email
            user.profile.save()
            messages.success(request, "Your account has been created! You are now able to log in")
            return redirect("dashboard")
    else:
        form = UserRegisterForm()
    return render(request, "account/register.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("dashboard")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, "account/profile.html", {"u_form": u_form, "p_form": p_form})
