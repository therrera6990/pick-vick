from django.core.management.base import BaseCommand

from fantasy.models import Player


class Command(BaseCommand):
    help = "Add sample NFL players for Pick Vick"

    def handle(self, *args, **options):
        players = [
            {
                "name": "Josh Allen",
                "position": "QB",
                "nfl_team": "BUF",
                "fantasy_points": 25.50,
            },
            {
                "name": "Saquon Barkley",
                "position": "RB",
                "nfl_team": "PHI",
                "fantasy_points": 21.75,
            },
            {
                "name": "Justin Jefferson",
                "position": "WR",
                "nfl_team": "MIN",
                "fantasy_points": 19.50,
            },
            {
                "name": "Travis Kelce",
                "position": "TE",
                "nfl_team": "KC",
                "fantasy_points": 16.25,
            },
        ]

        for player_data in players:
            player, created = Player.objects.get_or_create(
                name=player_data["name"],
                defaults={
                    "position": player_data["position"],
                    "nfl_team": player_data["nfl_team"],
                    "fantasy_points": player_data["fantasy_points"],
                    "available": True,
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added {player.name}"
                    )
                )
            else:
                self.stdout.write(
                    f"{player.name} already exists"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Pick Vick test data is ready."
            )
        )