from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FantasyTeamForm, PlayerForm, RegisterForm
from .models import FantasyTeam
from .models import FantasyTeam, Player


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

def player_list(request):
    players = Player.objects.all()

    search=request.GET.get("search", "")
    position = request.GET.get("position", "")

    if search:
        players = players.filter(name__icontains=search)

    if position:
        players = players.filter(position=position)

    context = {
        "players": players,
        "search": search,
        "position": position,
        "positions": Player.POSITION_CHOICES,
    }

    return render(
        request,
        "fantasy/player_list.html",
        context,
    )

def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    return render(
        request,
        "fantasy/player_detail.html",
        {"player": player},
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

@login_required
def player_delete(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":
        player.delete()
        return redirect("player_list")
    
    return render(
        request,
        "fantasy/player_confirm_delete.html",
        {"player": player},
    )

@login_required
def player_create(request):
    if request.method == "POST":
        form = PlayerForm(request.POST)

        if form.is_valid():
            player = form.save()
            return redirect("player_detail", player_id=player.id)
        
    else:
        form = PlayerForm()

    return render(
        request,
        "fantasy/player_form.html",
        {
            "form": form,
            "page_title": "Add Player",
        },
    )

@login_required
def player_edit(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    if request.method == "POST":
        form = PlayerForm(
            request.POST,
            instance=player,
        )

        if form.is_valid():
            form.save()
            return redirect(
                "player_detail",
                player_id=player.id,
            )
    else:
        form = PlayerForm(instance=player)

    return render(
        request,
        "fantasy/player_form.html",
        {
            "form": form,
            "page_title": "Edit Player",
        },
    )