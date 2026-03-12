from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register_view, name='register'),
    path('squad/', views.squad, name='squad'),
    path('set-entry/', views.set_entry, name='set_entry'),
    path('players/', views.players, name='players'),
    path('players/<int:player_id>/', views.player_details, name='player_details'),
    path("teams/", views.teams, name="teams"),
    path("teams/<int:team_id>/", views.team_details, name="team_details"),
    path('transfers/', views.transfers, name='transfers'),
    path('gameweeks/', views.gameweeks, name='gameweeks'),
    path('gameweeks/<int:gameweek_number>/', views.gameweek_details, name='gameweek_details'),
    path('cron/update_fpl/<str:token>/', views.update_fpl, name='update_fpl'),
]
