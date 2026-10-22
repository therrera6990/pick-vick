from django.conf import settings
from django.db import models

class League (models.Model):
    name = models.CharField(max_length=100)
    season = models.IntegerField()
    current_week = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class FantasyTeam(models.Model):
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name="teams"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fantasy_teams"
    )

    team_name =models.CharField(max_length=100)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    fantasy_points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name
    

class Player(models.Model):
    POSITION_CHOICES = [
        ("QB", "Quarterback"),
        ("RB", "Running Back"),
        ("WR", "Wide Receiver"),
        ("TE", "Tight End"),
        ("K", "Kicker"),
        ("DEF", "Defense"),
    ]

    name = models.CharField(max_length=100)
    position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES
    )

    nfl_team = models.CharField(max_length=50)
    fantasy_points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.position})"
    

class Roster(models.Model):
    ROSTER_POSITION_CHOICES = [
        ("STARTER", "Starter"),
        ("BENCH", "Bench"),
    ]

    fantasy_team= models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="roster_entries"
    )


    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        related_name="roster_entry"
    )

    roster_position = models.CharField(
        max_length=20,
        choices=ROSTER_POSITION_CHOICES,
        default="BENCH"
    )

    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name} - {self.fantasy_team.team_name}"


class Matchup(models.Model):
    week = models.IntegerField()

    home_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="home_matchups"
    )

    away_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="away_matchups"
    )

    home_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    away_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Week {self.week}: {self.home_team} vs {self.away_team}"


class Transaction(models.Model):
    TRANSACTION_CHOICES = [
        ("ADD", "Add"),
        ("DROP", "Drop"),
    ]

    fantasy_team = models.ForeignKey(
        FantasyTeam,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return (
            f"{self.fantasy_team.team_name} "
            f"{self.transaction_type} "
            f"{self.player.name}"
        )