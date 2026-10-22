from django.contrib import admin

from .models import(
    League,
    FantasyTeam,
    Player,
    Roster,
    Matchup,
    Transaction,
)

admin.site.register(League)
admin.site.register(FantasyTeam)
admin.site.register(Player)
admin.site.register(Roster)
admin.site.register(Matchup)
admin.site.register(Transaction)

