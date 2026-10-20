from django.db import models
from django.db import settings

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
