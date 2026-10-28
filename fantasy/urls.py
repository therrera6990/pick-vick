from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("register/", views.register, name="register"),

    path("players/", views.player_list, name="player_list"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="fantasy/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("teams/", views.team_list, name="team_list"),

    path(
        "players/create/",
         views.player_create,
          name="player_create",
    ),

    path(
        "teams/create/",
        views.team_create,
        name="team_create",
    ),

    path(
        "teams/<int:team_id>/",
        views.team_detail,
        name="team_detail",
    ),

    path(
         "players/<int:player_id>/",
         views.player_detail,
         name="player_detail",
    ),

    path(
        "teams/<int:team_id>/edit/",
        views.team_edit,
        name="team_edit",
    ),

    path(
        "teams/<int:team_id>/delete/",
        views.team_delete,
        name="team_delete",
    ),
]