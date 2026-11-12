from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import FantasyTeam, League, Player, Roster, Matchup


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
            float(self.player.fantasy_points),
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

    def test_search_players_by_name(self):
        response = self.client.get(
            reverse("player_list"),
            {
                "search": "Josh",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Josh Allen")

    def test_filter_players_by_position(self):
        response = self.client.get(
            reverse("player_list"),
            {
                "position": "QB",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Josh Allen")

    def test_filter_players_by_nfl_team(self):
        response = self.client.get(
            reverse("player_list"),
            {
                "nfl_team": "BUF",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Josh Allen")

    def test_filter_players_by_availability(self):
        response = self.client.get(
            reverse("player_list"),
            {
                "availability": "available",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Josh Allen")

    def test_combined_player_filters(self):
        response = self.client.get(
            reverse("player_list"),
            {
                "search": "Josh",
                "position": "QB",
                "nfl_team": "BUF",
                "availability": "available",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Josh Allen")

class MatchupTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="matchupuser",
            password="testpass123",
        )

        self.league = League.objects.create(
            name="Test League",
            season=2026,
            current_week=1,
        )

        self.home_team = FantasyTeam.objects.create(
            league=self.league,
            owner=self.user,
            team_name="Home Team",
            wins=0,
            losses=0,
            fantasy_points=0,
        )

        self.away_team = FantasyTeam.objects.create(
            league=self.league,
            owner=self.user,
            team_name="Away Team",
            wins=0,
            losses=0,
            fantasy_points=0,
        )

        self.matchup = Matchup.objects.create(
            week=1,
            home_team=self.home_team,
            away_team=self.away_team,
            home_score=0,
            away_score=0,
            completed=False,
        )

    def test_matchup_list_loads(self):
        response = self.client.get(
            reverse("matchup_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Home Team",
        )

        self.assertContains(
            response,
            "Away Team",
        )

    def test_logged_in_user_can_create_matchup(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        response = self.client.post(
            reverse("matchup_create"),
            {
                "week": 2,
                "home_team": self.home_team.id,
                "away_team": self.away_team.id,
            },
        )

        self.assertEqual(
            Matchup.objects.count(),
            2,
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_team_cannot_play_itself(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        response = self.client.post(
            reverse("matchup_create"),
            {
                "week": 2,
                "home_team": self.home_team.id,
                "away_team": self.home_team.id,
            },
        )

        self.assertEqual(
            Matchup.objects.count(),
            1,
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_score_can_be_entered(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "120.50",
                "away_score": "100.25",
                "completed": True,
            },
        )

        self.matchup.refresh_from_db()

        self.assertEqual(
            float(self.matchup.home_score),
            120.50,
        )

        self.assertEqual(
            float(self.matchup.away_score),
            100.25,
        )

        self.assertTrue(
            self.matchup.completed
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_completed_matchup_updates_wins_and_losses(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "120.00",
                "away_score": "100.00",
                "completed": True,
            },
        )

        self.home_team.refresh_from_db()
        self.away_team.refresh_from_db()

        self.assertEqual(
            self.home_team.wins,
            1,
        )

        self.assertEqual(
            self.away_team.losses,
            1,
        )

    def test_completed_matchup_updates_fantasy_points(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "125.00",
                "away_score": "110.00",
                "completed": True,
            },
        )

        self.home_team.refresh_from_db()
        self.away_team.refresh_from_db()

        self.assertEqual(
            float(self.home_team.fantasy_points),
            125.00,
        )

        self.assertEqual(
            float(self.away_team.fantasy_points),
            110.00,
        )

    def test_updating_completed_matchup_does_not_double_count(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "120.00",
                "away_score": "100.00",
                "completed": True,
            },
        )

        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "125.00",
                "away_score": "105.00",
                "completed": True,
            },
        )

        self.home_team.refresh_from_db()
        self.away_team.refresh_from_db()

        self.assertEqual(
            self.home_team.wins,
            1,
        )

        self.assertEqual(
            self.away_team.losses,
            1,
        )

        self.assertEqual(
            float(self.home_team.fantasy_points),
            125.00,
        )

        self.assertEqual(
            float(self.away_team.fantasy_points),
            105.00,
        )

    def test_updating_score_can_change_winner(self):
        self.client.login(
            username="matchupuser",
            password="testpass123",
        )

        # Home team wins first.
        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "120.00",
                "away_score": "100.00",
                "completed": True,
            },
        )

        # Change the score so the away team wins.
        self.client.post(
            reverse(
                "matchup_score_edit",
                args=[self.matchup.id],
            ),
            {
                "home_score": "95.00",
                "away_score": "110.00",
                "completed": True,
            },
        )

        self.home_team.refresh_from_db()
        self.away_team.refresh_from_db()

        self.assertEqual(
            self.home_team.wins,
            0,
        )

        self.assertEqual(
            self.home_team.losses,
            1,
        )

        self.assertEqual(
            self.away_team.wins,
            1,
        )

        self.assertEqual(
            self.away_team.losses,
            0,
        )

    def test_standings_page_loads(self):
        response = self.client.get(
            reverse("standings")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertContains(
            response,
            "Home Team",
        )

        self.assertContains(
            response,
            "Away Team",
        )
    
class RosterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rosteruser",
            password="testpass123",
        )

        self.league = League.objects.create(
            name="Test League",
            season=2026,
            current_week=1,
        )

        self.team = FantasyTeam.objects.create(
            league=self.league,
            owner=self.user,
            team_name="Roster Test Team",
        )

        self.player = Player.objects.create(
            name="Test Player",
            position="RB",
            nfl_team="TEST",
            fantasy_points=10.00,
            available=True,
        )

    def test_roster_page_loads_for_owner(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "team_roster",
                args=[self.team.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_can_add_player_to_roster(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "roster_add_player",
                args=[self.team.id],
            ),
            {
                "player_id": self.player.id,
                "roster_position": "BENCH",
            },
        )

        self.assertEqual(Roster.objects.count(), 1)

        self.player.refresh_from_db()
        self.assertFalse(self.player.available)

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_toggle_roster_position(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        roster_entry = Roster.objects.create(
            fantasy_team=self.team,
            player=self.player,
            roster_position="BENCH",
        )

        response = self.client.post(
            reverse(
                "roster_toggle_position",
                args=[
                    self.team.id,
                    roster_entry.id,
                ],
            )
        )

        roster_entry.refresh_from_db()

        self.assertEqual(
            roster_entry.roster_position,
            "STARTER",
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_drop_player(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        self.player.available = False
        self.player.save()

        roster_entry = Roster.objects.create(
            fantasy_team=self.team,
            player=self.player,
            roster_position="STARTER",
        )

        response = self.client.post(
            reverse(
                "roster_drop_player",
                args=[
                    self.team.id,
                    roster_entry.id,
                ],
            )
        )

        self.assertEqual(Roster.objects.count(), 0)

        self.player.refresh_from_db()
        self.assertTrue(self.player.available)

        self.assertEqual(response.status_code, 302)

class RosterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rosteruser",
            password="testpass123",
        )

        self.league = League.objects.create(
            name="Test League",
            season=2026,
            current_week=1,
        )

        self.team = FantasyTeam.objects.create(
            league=self.league,
            owner=self.user,
            team_name="Roster Test Team",
        )

        self.player = Player.objects.create(
            name="Test Player",
            position="RB",
            nfl_team="TEST",
            fantasy_points=10.00,
            available=True,
        )

    def test_roster_page_loads_for_owner(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "team_roster",
                args=[self.team.id],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_logged_in_user_can_add_player_to_roster(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        response = self.client.post(
            reverse(
                "roster_add_player",
                args=[self.team.id],
            ),
            {
                "player_id": self.player.id,
                "roster_position": "BENCH",
            },
        )

        self.assertEqual(Roster.objects.count(), 1)

        self.player.refresh_from_db()
        self.assertFalse(self.player.available)

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_toggle_roster_position(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        roster_entry = Roster.objects.create(
            fantasy_team=self.team,
            player=self.player,
            roster_position="BENCH",
        )

        response = self.client.post(
            reverse(
                "roster_toggle_position",
                args=[
                    self.team.id,
                    roster_entry.id,
                ],
            )
        )

        roster_entry.refresh_from_db()

        self.assertEqual(
            roster_entry.roster_position,
            "STARTER",
        )

        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_drop_player(self):
        self.client.login(
            username="rosteruser",
            password="testpass123",
        )

        self.player.available = False
        self.player.save()

        roster_entry = Roster.objects.create(
            fantasy_team=self.team,
            player=self.player,
            roster_position="STARTER",
        )

        response = self.client.post(
            reverse(
                "roster_drop_player",
                args=[
                    self.team.id,
                    roster_entry.id,
                ],
            )
        )

        self.assertEqual(Roster.objects.count(), 0)

        self.player.refresh_from_db()
        self.assertTrue(self.player.available)

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