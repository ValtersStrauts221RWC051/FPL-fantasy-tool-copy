from django.contrib import admin
from fantasy.models import User, Team, Position, Gameweek, Player
# Register your models here.

admin.site.register(User)
admin.site.register(Team) 
admin.site.register(Position)
admin.site.register(Gameweek)
admin.site.register(Player)
