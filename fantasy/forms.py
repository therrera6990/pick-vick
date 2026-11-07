from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import FantasyTeam, Player


class RegisterForm(UserCreationForm):
    email = User._meta.get_field("email").formfield(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]


class FantasyTeamForm(forms.ModelForm):
    class Meta:
        model = FantasyTeam
        fields = [
            "league",
            "team_name",
        ]


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            "name",
            "position",
            "nfl_team",
            "fantasy_points",
            "available",
        ]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()

        if len(name) < 2:
            raise forms.ValidationError(
                "Player name must be at least 2 characters long."
            )

        return name

    def clean_nfl_team(self):
        nfl_team = self.cleaned_data["nfl_team"].strip().upper()

        if len(nfl_team) < 2 or len(nfl_team) > 4:
            raise forms.ValidationError(
                "NFL team abbreviation must be between 2 and 4 characters."
            )

        return nfl_team

    def clean_fantasy_points(self):
        fantasy_points = self.cleaned_data["fantasy_points"]

        if fantasy_points < 0:
            raise forms.ValidationError(
                "Fantasy points cannot be negative."
            )

        return fantasy_points