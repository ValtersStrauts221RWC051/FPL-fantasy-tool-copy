from django.core.management.base import BaseCommand
import requests

from fantasy.models import Team, Position, Gameweek, Player


class Command(BaseCommand):
    help = "Import FPL bootstrap data"

    def handle(self, *args, **kwargs):
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        data = requests.get(url).json()

        self.import_teams(data["teams"])
        self.import_positions(data["element_types"])
        self.import_gameweeks(data["events"])
        self.import_players(data["elements"])

        self.stdout.write(self.style.SUCCESS("FPL data imported successfully"))


    def import_teams(self, teams):
        for team in teams:
            Team.objects.update_or_create(
                fpl_id=team["id"],
                defaults={
                    "name": team["name"],
                    "short_name": team["short_name"],
                    "strength": team["strength"],
                    "strength_overall_home": team["strength_overall_home"],
                    "strength_overall_away": team["strength_overall_away"],
                }
            )


    def import_positions(self, positions):
        for pos in positions:
            Position.objects.update_or_create(
                fpl_id=pos["id"],
                defaults={
                    "name": pos["singular_name"],
                    "short_name": pos["singular_name_short"],
                    "squad_select": pos["squad_select"],
                    "squad_min_play": pos["squad_min_play"],
                    "squad_max_play": pos["squad_max_play"],
                }
            )


    def import_gameweeks(self, events):
        for event in events:
            Gameweek.objects.update_or_create(
                fpl_id=event["id"],
                defaults={
                    "name": event["name"],
                    "deadline_time": event["deadline_time"],
                    "finished": event["finished"],
                    "is_current": event["is_current"],
                    "is_next": event["is_next"],
                }
            )


    def import_players(self, players):
        for p in players:
            team = Team.objects.get(fpl_id=p["team"])
            position = Position.objects.get(fpl_id=p["element_type"])

            Player.objects.update_or_create(
                fpl_id=p["id"],
                defaults={
                    "player_code": p.get("opta_code"),
                    "web_name": p["web_name"],
                    "first_name": p.get("first_name"),
                    "second_name": p.get("second_name"),

                    "team": team,
                    "position": position,

                    "now_cost": p["now_cost"],
                    "total_points": p["total_points"],
                    "status": p["status"],

                    # Basic stats
                    "minutes": p["minutes"],
                    "goals_scored": p["goals_scored"],
                    "assists": p["assists"],
                    "clean_sheets": p["clean_sheets"],
                    "goals_conceded": p["goals_conceded"],
                    "saves": p["saves"],
                    "bonus": p["bonus"],
                    "bps": p["bps"],

                    # Discipline
                    "yellow_cards": p["yellow_cards"],
                    "red_cards": p["red_cards"],
                    "own_goals": p["own_goals"],
                    "penalties_missed": p["penalties_missed"],
                    "penalties_saved": p["penalties_saved"],

                    # Advanced stats (FPL returns strings!)
                    "influence": float(p["influence"] or 0),
                    "creativity": float(p["creativity"] or 0),
                    "threat": float(p["threat"] or 0),
                    "defensive_contribution": p.get("defensive_contribution", 0),

                    "expected_goals": float(p["expected_goals"] or 0),
                    "expected_assists": float(p["expected_assists"] or 0),
                    "expected_goal_involvements": float(p["expected_goal_involvements"] or 0),
                    "expected_goals_conceded": float(p["expected_goals_conceded"] or 0),

                    # Form & availability
                    "form": float(p["form"] or 0),
                    "points_per_game": float(p["points_per_game"] or 0),
                    "chance_of_playing_this_round": p.get("chance_of_playing_this_round"),
                    "chance_of_playing_next_round": p.get("chance_of_playing_next_round"),
                }
            )
