from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FantasyTeamForm, MatchupForm, MatchupScoreForm, PlayerForm, RegisterForm
from .models import FantasyTeam, League, Matchup, Player, Roster


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

    search = request.GET.get("search", "")
    position = request.GET.get("position", "")
    nfl_team = request.GET.get("nfl_team", "")
    availability = request.GET.get("availability", "")

    if search:
        players = players.filter(name__icontains=search)

    if position:
        players = players.filter(position=position)

    if nfl_team:
        players = players.filter(nfl_team__iexact=nfl_team)

    if availability == "available":
        players = players.filter(available=True)

    elif availability == "unavailable":
        players = players.filter(available=False)

    nfl_teams = (
        Player.objects
        .exclude(nfl_team="")
        .values_list("nfl_team", flat=True)
        .distinct()
        .order_by("nfl_team")
    )

    context = {
        "players": players,
        "search": search,
        "position": position,
        "nfl_team": nfl_team,
        "availability": availability,
        "positions": Player.POSITION_CHOICES,
        "nfl_teams": nfl_teams,
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

def matchup_list(request):
    matchups = Matchup.objects.select_related(
        "home_team",
        "away_team",
    ).order_by("week", "id")

    return render(
        request,
        "fantasy/matchup_list.html",
        {
            "matchups": matchups,
        },
    )

@login_required
def matchup_create(request):
    if request.method == "POST":
        form = MatchupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("matchup_list")

    else:
        form = MatchupForm()

    return render(
        request,
        "fantasy/matchup_form.html",
        {
            "form": form,
        },
    )

@login_required
def matchup_score_edit(request, matchup_id):
    matchup = get_object_or_404(
        Matchup,
        id=matchup_id,
    )

    if request.method == "POST":
        # Save the old matchup values before changing anything.
        old_completed = matchup.completed
        old_home_score = matchup.home_score
        old_away_score = matchup.away_score

        form = MatchupScoreForm(
            request.POST,
            instance=matchup,
        )

        if form.is_valid():
            home_team = matchup.home_team
            away_team = matchup.away_team

            # If this matchup was already completed,
            # remove its old result before applying the new one.
            if old_completed:
                if old_home_score > old_away_score:
                    home_team.wins -= 1
                    away_team.losses -= 1

                elif old_away_score > old_home_score:
                    away_team.wins -= 1
                    home_team.losses -= 1

                home_team.fantasy_points -= old_home_score
                away_team.fantasy_points -= old_away_score

            matchup = form.save()

            # Apply the new result if the matchup is completed.
            if matchup.completed:
                if matchup.home_score > matchup.away_score:
                    home_team.wins += 1
                    away_team.losses += 1

                elif matchup.away_score > matchup.home_score:
                    away_team.wins += 1
                    home_team.losses += 1

                home_team.fantasy_points += matchup.home_score
                away_team.fantasy_points += matchup.away_score

            home_team.save()
            away_team.save()

            return redirect("matchup_list")

    else:
        form = MatchupScoreForm(
            instance=matchup,
        )

    return render(
        request,
        "fantasy/matchup_score_form.html",
        {
            "form": form,
            "matchup": matchup,
        },
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
def team_roster(request, team_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    roster_entries = Roster.objects.filter(
        fantasy_team=team
    ).select_related("player")

    starters = roster_entries.filter(
        roster_position="STARTER"
    )

    bench = roster_entries.filter(
        roster_position="BENCH"
    )

    return render(
        request,
        "fantasy/team_roster.html",
        {
            "team": team,
            "starters": starters,
            "bench": bench,
        },
    )

@login_required
def roster_add_player(request, team_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    available_players = Player.objects.filter(
        available=True,
        roster_entry__isnull=True,
    )

    if request.method == "POST":
        player_id = request.POST.get("player_id")
        roster_position = request.POST.get(
            "roster_position",
            "BENCH",
        )

        player = get_object_or_404(
            Player,
            id=player_id,
            available=True,
            roster_entry__isnull=True,
        )

        Roster.objects.create(
            fantasy_team=team,
            player=player,
            roster_position=roster_position,
        )

        player.available = False
        player.save()

        return redirect(
            "team_roster",
            team_id=team.id,
        )

    return render(
        request,
        "fantasy/roster_add_player.html",
        {
            "team": team,
            "available_players": available_players,
        },
    )

@login_required
def roster_drop_player(request, team_id, roster_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    roster_entry = get_object_or_404(
        Roster,
        id=roster_id,
        fantasy_team=team,
    )

    if request.method == "POST":
        player = roster_entry.player

        roster_entry.delete()

        player.available = True
        player.save()

        return redirect(
            "team_roster",
            team_id=team.id,
        )

    return render(
        request,
        "fantasy/roster_confirm_drop.html",
        {
            "team": team,
            "roster_entry": roster_entry,
        },
    )

@login_required
def roster_toggle_position(request, team_id, roster_id):
    team = get_object_or_404(
        FantasyTeam,
        id=team_id,
        owner=request.user,
    )

    roster_entry = get_object_or_404(
        Roster,
        id=roster_id,
        fantasy_team=team,
    )

    if request.method == "POST":
        if roster_entry.roster_position == "STARTER":
            roster_entry.roster_position = "BENCH"
        else:
            roster_entry.roster_position = "STARTER"

        roster_entry.save()

    return redirect(
        "team_roster",
        team_id=team.id,
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