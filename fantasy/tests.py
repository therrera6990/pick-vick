from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import FantasyTeam, League, Player


class HomePageTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)


class AuthenticationTests(TestCase):
    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

class PlayerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="playeruser",
            password="testpass123",
        )

        self.player = Player.objects.create(
            name="Josh Allen",
            position="QB",
            nfl_team="BUF",
            fantasy_points=24.50,
            available=True,
        )

    def test_player_list_loads(self):
        response = self.client.get(reverse("player_list"))
        self.assertEqual(response.status_code, 200)

    def test_player_detail_loads(self):
        response = self.client.get(
            reverse(
                "player_detail",
                args=[self.player.id],
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_can_create_player(self):
        self.client.login(
            username="playeruser",
            password="testpass123",
        )

        response = self.client.post(
            reverse("player_create"),
            {
                "name": "Saquon Barkley",
                "position": "RB",
                "nfl_team": "PHI",
                "fantasy_points": "20.00",
                "available": True,
            },
        )

        self.assertEqual(Player.objects.count(), 2)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_edit_player(self):
        self.client.login(
            username="playeruser",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "player_edit",
                args=[self.player.id],
            ),
            {
                "name": "Josh Allen",
                "position": "QB",
                "nfl_team": "BUF",
                "fantasy_points": "30.00",
                "available": True,
            },
        )

        self.player.refresh_from_db()

        self.assertEqual(
            self.player.fantasy_points,
            30.00,
        )
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_delete_player(self):
        self.client.login(
            username="playeruser",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "player_delete",
                args=[self.player.id],
            )
        )

        self.assertEqual(Player.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

        
class FantasyTeamTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.league = League.objects.create(
            name="Pick Vick League",
            season=2026,
            current_week=1,
        )

        self.team = FantasyTeam.objects.create(
            league=self.league,
            owner=self.user,
            team_name="Test Team",
        )

    def test_team_list_loads(self):
        response = self.client.get(reverse("team_list"))
        self.assertEqual(response.status_code, 200)

    def test_team_detail_loads(self):
        response = self.client.get(
            reverse("team_detail", args=[self.team.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_can_create_team(self):
        self.client.login(
            username="testuser",
            password="testpass123",
        )

        response = self.client.post(
            reverse("team_create"),
            {
                "league": self.league.id,
                "team_name": "New Team",
            },
        )

        self.assertEqual(FantasyTeam.objects.count(), 2)
        self.assertEqual(response.status_code, 302)