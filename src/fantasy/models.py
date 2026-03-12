from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    fpl_team_id = models.IntegerField(null=True, blank=True)


class Team(models.Model):
    fpl_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=5)
    strength = models.IntegerField()
    strength_overall_home = models.IntegerField()
    strength_overall_away = models.IntegerField()

    def __str__(self):
        return self.name


class Position(models.Model):
    fpl_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=20)
    short_name = models.CharField(max_length=5)
    squad_select = models.IntegerField()
    squad_min_play = models.IntegerField(null=True)
    squad_max_play = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class Gameweek(models.Model):
    fpl_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=20)
    deadline_time = models.DateTimeField()
    finished = models.BooleanField()
    is_current = models.BooleanField()
    is_next = models.BooleanField()

    @property
    def status(self):
        if self.is_current:
            return "Current"
        if self.is_next:
            return "Next"
        if self.finished:
            return "Finished"
        return "Upcoming"
    
    def __str__(self):
        return self.name


class Player(models.Model):
    fpl_id = models.IntegerField(unique=True)
    web_name = models.CharField(max_length=50)
    player_code = models.CharField(max_length=20, null=True)

    first_name = models.CharField(max_length=50, null=True)
    second_name = models.CharField(max_length=50, null=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    now_cost = models.IntegerField()
    total_points = models.IntegerField()
    status = models.CharField(max_length=1)

    # Performance
    minutes = models.IntegerField(default=0)
    goals_scored = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    bps = models.IntegerField(default=0)

    # Discipline
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)
    own_goals = models.IntegerField(default=0)
    penalties_missed = models.IntegerField(default=0)
    penalties_saved = models.IntegerField(default=0)

    # Advanced stats
    influence = models.FloatField(default=0)
    creativity = models.FloatField(default=0)
    threat = models.FloatField(default=0)
    defensive_contribution = models.IntegerField(default=0)

    expected_goals = models.FloatField(default=0)
    expected_assists = models.FloatField(default=0)
    expected_goal_involvements = models.FloatField(default=0)
    expected_goals_conceded = models.FloatField(default=0)

    # Form & availability
    form = models.FloatField(default=0)
    points_per_game = models.FloatField(default=0)
    chance_of_playing_this_round = models.IntegerField(null=True)
    chance_of_playing_next_round = models.IntegerField(null=True)

    @property
    def price(self):
        return self.now_cost / 10
    
    def __str__(self):
        return f"{self.first_name} '{self.second_name}' ({self.web_name})"