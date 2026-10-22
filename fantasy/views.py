from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FantasyTeamForm, RegisterForm
from .models import FantasyTeam


def home(request):
    return render(request, "fantasy/home.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "fantasy/register.html",
        {"form": form},
    )


def team_list(request):
    teams = FantasyTeam.objects.all()

    return render(
        request,
        "fantasy/team_list.html",
        {"teams": teams},
    )


@login_required
def team_create(request):
    if request.method == "POST":
        form = FantasyTeamForm(request.POST)

        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()

            return redirect("team_detail", team_id=team.id)
    else:
        form = FantasyTeamForm()

    return render(
        request,
        "fantasy/team_form.html",
        {
            "form": form,
            "page_title": "Create Fantasy Team",
        },
    )


def team_detail(request, team_id):
    team = get_object_or_404(FantasyTeam, id=team_id)

    return render(
        request,
        "fantasy/team_detail.html",
        {"team": team},
    )


@login_required
def team_edit(request, team_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    if request.method == "POST":
        form = FantasyTeamForm(
            request.POST,
            instance=team,
        )

        if form.is_valid():
            form.save()
            return redirect("team_detail", team_id=team.id)
    else:
        form = FantasyTeamForm(instance=team)

    return render(
        request,
        "fantasy/team_form.html",
        {
            "form": form,
            "page_title": "Edit Fantasy Team",
        },
    )


@login_required
def team_delete(request, team_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    if request.method == "POST":
        team.delete()
        return redirect("team_list")

    return render(
        request,
        "fantasy/team_confirm_delete.html",
        {"team": team},
    )