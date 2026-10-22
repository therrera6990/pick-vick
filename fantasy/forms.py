from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FantasyTeam


class RegisterForm(UserCreationForm):
    email = User._meta.get_field("email").formfield(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class FantasyTeamForm(forms.ModelForm):
    class Meta:
        model = FantasyTeam
        fields = ["league", "team_name"]