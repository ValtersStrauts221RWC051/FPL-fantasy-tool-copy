from collections import Counter
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.core.management import call_command
from django.conf import settings

import os
import requests

from fantasy.models import User, Team, Position, Gameweek, Player
from fantasy.predictions import predict_player_points


def _generate_predictions(player_id):
    player = get_object_or_404(Player, fpl_id=player_id)
    if player.status in ['i', 'u', 'd', 'n']:
        return 0.00  # No prediction for injured/unavailable players
    pred_points = max(predict_player_points(player), 0.00)
    return round(pred_points, 2)


def _resolve_entry_id(request):
    entry_id_param = request.GET.get("entry_id")
    session_entry = request.session.get("fpl_entry_id")

    if entry_id_param:
        try:
            entry_id = int(entry_id_param)
            request.session["fpl_entry_id"] = entry_id
            return entry_id
        except ValueError:
            return None

    if session_entry:
        return session_entry

    env_default = os.getenv("FPL_ENTRY_ID")
    return int(env_default) if env_default else None


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'fantasy/home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home') 
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    
    return render(request, 'fantasy/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        password_confirmation = request.POST.get('pwd_c')

        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'fantasy/register.html')


@login_required
def squad(request):
    entry_id_param = request.GET.get("entry_id")
    session_entry = request.session.get("fpl_entry_id")

    entry_id = None
    if entry_id_param:
        try:
            entry_id = int(entry_id_param)
            request.session["fpl_entry_id"] = entry_id  # remember for navigation
        except ValueError:
            pass
    elif session_entry:
        entry_id = session_entry
    else:
        # fallback to env default if provided
        env_default = os.getenv("FPL_ENTRY_ID")
        entry_id = int(env_default) if env_default else None

    bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

    squad = []
    meta = {}
    error_message = None

    if not entry_id:
        error_message = "No FPL Team ID set. Add your ID to view your squad."
        return render(request, 'fantasy/squad.html', {
            'squad': squad,
            'meta': meta,
            'error_message': error_message,
        })

    try:
        bootstrap = requests.get(bootstrap_url, timeout=10)
        bootstrap.raise_for_status()
        bootstrap_data = bootstrap.json()

        # Find the active or next gameweek
        events = bootstrap_data.get("events", [])
        current_event = next((e for e in events if e.get("is_current")), None)
        if not current_event:
            current_event = next((e for e in events if e.get("is_next")), None)
        if not current_event and events:
            current_event = events[0]

        if not current_event:
            raise ValueError("Unable to determine current gameweek.")

        gw_id = current_event["id"]

        # Fetch entry info and picks for the gameweek
        entry_info = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{entry_id}/",
            timeout=10,
        )
        entry_info.raise_for_status()
        entry_data = entry_info.json()

        history_response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/",
            timeout=10,
        )
        history_response.raise_for_status()
        history_data = history_response.json()

        picks_response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{gw_id}/picks/",
            timeout=10,
        )
        picks_response.raise_for_status()
        picks_data = picks_response.json()

        elements = {el["id"]: el for el in bootstrap_data.get("elements", [])}
        teams = {t["id"]: t for t in bootstrap_data.get("teams", [])}
        positions = {p["id"]: p for p in bootstrap_data.get("element_types", [])}

        for pick in picks_data.get("picks", []):
            element = elements.get(pick["element"])
            if not element:
                continue

            team_info = teams.get(element["team"])
            position_info = positions.get(element["element_type"])

            full_name = f"{element.get('first_name', '')} {element.get('second_name', '')}".strip()
            if not full_name:
                full_name = element.get("web_name", "Unknown")

            squad.append({
                "id": element["id"],
                "name": full_name,
                "web_name": element.get("web_name"),
                "team": team_info.get("name") if team_info else "Unknown",
                "position": position_info.get("singular_name_short") if position_info else "N/A",
                "points": element.get("event_points", 0),
                "total_points": element.get("total_points", 0),
                "price": element.get("now_cost", 0) / 10,
                "predicted_points": _generate_predictions(element['id']),
                "is_captain": pick.get("is_captain", False),
                "is_vice_captain": pick.get("is_vice_captain", False),
                "is_starting": pick.get("multiplier", 0) > 0,
                "multiplier": pick.get("multiplier", 0),
            })

        # Start players first, then bench; within that order by position id
        position_order = {p["id"]: idx for idx, p in enumerate(bootstrap_data.get("element_types", []))}
        squad.sort(key=lambda p: (
            not p["is_starting"],
            position_order.get(elements[p["id"]]["element_type"], 99) if p["id"] in elements else 99,
            -p["total_points"],
        ))

        entry_history = picks_data.get("entry_history", {})

        # Calculate free transfers from public history with current season cap.
        game_settings = bootstrap_data.get("game_settings", {})
        max_extra = int(game_settings.get("max_extra_free_transfers", 1))
        base_cap = 1 + max_extra
        finished_events = [
            event["id"]
            for event in bootstrap_data.get("events", [])
            if event.get("finished")
        ]
        finished_events.sort()

        # AFCON bonus added after GW15 deadline (applies ahead of GW16).
        bonus_rules = {16: {"bonus": 5, "cap_extra": 5}}
        history_current = {
            row["event"]: row for row in history_data.get("current", [])
        }
        
        # Build chips lookup from the separate chips array
        chips_by_event = {
            chip["event"]: chip["name"] for chip in history_data.get("chips", [])
        }

        free_transfers = 1
        for event_id in finished_events:
            cap_for_event = base_cap
            bonus = 0
            cap_extra = 0
            if event_id in bonus_rules:
                bonus = bonus_rules[event_id]["bonus"]
                cap_extra = bonus_rules[event_id]["cap_extra"]

            cap_for_event = cap_for_event + cap_extra
            free_transfers = min(free_transfers + bonus, cap_for_event)

            row = history_current.get(event_id, {})
            transfers_used = row.get("event_transfers", 0) or 0
            
            # Get chip from the chips lookup (NOT from the row)
            chip = chips_by_event.get(event_id)

            remaining = max(0, free_transfers - transfers_used)
            if chip in ("freehit", "wildcard"):
                free_transfers = 1
            else:
                free_transfers = min(base_cap, remaining + 1)

        meta = {
            "gameweek": gw_id,
            "gameweek_name": current_event.get("name"),
            "entry_id": entry_id,
            "team_name": entry_data.get("name"),
            "player_name": f"{entry_data.get('player_first_name', '')} {entry_data.get('player_last_name', '')}".strip(),
            "bank": entry_history.get("bank", 0) / 10,
            "value": entry_history.get("value", 0) / 10,
            "points": entry_history.get("points"),
            "free_transfers": free_transfers,
        }
    except Exception as exc:  # noqa: BLE001
        error_message = f"Could not load FPL squad: {exc}"

    return render(request, 'fantasy/squad.html', {
        'squad': squad,
        'meta': meta,
        'entry_id': entry_id,
        'error_message': error_message,
    })


@login_required
def set_entry(request):
    if request.method == "POST":
        entry_id_raw = request.POST.get("entry_id")
        try:
            entry_id = int(entry_id_raw)
            request.session["fpl_entry_id"] = entry_id
            messages.success(request, f"FPL Team ID set to {entry_id}.")
            return redirect('squad')
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid numeric FPL Team ID.")

    return render(request, "fantasy/set_entry.html")


@login_required
def players(request):
    players = list(
        Player.objects
        .select_related("team", "position")
        .order_by("-total_points")
    )

    teams = Team.objects.all()
    positions = Position.objects.all()
    return render(request, "fantasy/players.html", {
        "players": players,
        "teams": teams,
        "positions": positions,
    })


@login_required
def player_details(request, player_id):
    player = get_object_or_404(
        Player.objects.select_related("team", "position"),
        fpl_id=player_id
    )

    player.predicted_score = _generate_predictions(player.fpl_id)

    return render(request, "fantasy/player_details.html", {"player": player})


@login_required
def transfers(request):
    entry_id = _resolve_entry_id(request)
    context = {
        "transfer_window_open": True,
        "recommended_transfers": [],
        "strategies": [],
        "top_predicted_players": [],
        "budget": 0,
        "free_transfers": 0,
        "error_message": None,
    }

    if not entry_id:
        context["error_message"] = "No FPL Team ID set. Add your ID to see tailored transfers."
        return render(request, "fantasy/transfers.html", context)

    try:
        bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        bootstrap = requests.get(bootstrap_url, timeout=10)
        bootstrap.raise_for_status()
        bootstrap_data = bootstrap.json()

        events = bootstrap_data.get("events", [])
        current_event = next((e for e in events if e.get("is_current")), None)
        if not current_event:
            current_event = next((e for e in events if e.get("is_next")), None)
        if not current_event and events:
            current_event = events[0]

        if not current_event:
            raise ValueError("Unable to determine current gameweek.")

        gw_id = current_event["id"]

        picks_response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{gw_id}/picks/",
            timeout=10,
        )
        picks_response.raise_for_status()
        picks_data = picks_response.json()

        history_response = requests.get(
            f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/",
            timeout=10,
        )
        history_response.raise_for_status()
        history_data = history_response.json()

        elements = {el["id"]: el for el in bootstrap_data.get("elements", [])}
        teams = {t["id"]: t for t in bootstrap_data.get("teams", [])}
        positions = {p["id"]: p for p in bootstrap_data.get("element_types", [])}
        game_settings = bootstrap_data.get("game_settings", {})
        team_limit = int(game_settings.get("squad_team_limit", 3))

        entry_history = picks_data.get("entry_history", {})
        budget = entry_history.get("bank", 0) / 10

        max_extra = int(game_settings.get("max_extra_free_transfers", 1))
        base_cap = 1 + max_extra
        finished_events = [
            event["id"]
            for event in bootstrap_data.get("events", [])
            if event.get("finished")
        ]
        finished_events.sort()

        bonus_rules = {16: {"bonus": 5, "cap_extra": 5}}
        history_current = {
            row["event"]: row for row in history_data.get("current", [])
        }

        chips_by_event = {
            chip["event"]: chip["name"] for chip in history_data.get("chips", [])
        }

        free_transfers = 1
        for event_id in finished_events:
            cap_for_event = base_cap
            bonus = 0
            cap_extra = 0
            if event_id in bonus_rules:
                bonus = bonus_rules[event_id]["bonus"]
                cap_extra = bonus_rules[event_id]["cap_extra"]

            cap_for_event = cap_for_event + cap_extra
            free_transfers = min(free_transfers + bonus, cap_for_event)

            row = history_current.get(event_id, {})
            transfers_used = row.get("event_transfers", 0) or 0

            chip = chips_by_event.get(event_id)

            remaining = max(0, free_transfers - transfers_used)
            if chip in ("freehit", "wildcard"):
                free_transfers = 1
            else:
                free_transfers = min(base_cap, remaining + 1)

        squad_players = []
        for pick in picks_data.get("picks", []):
            element = elements.get(pick["element"])
            if not element:
                continue

            team_info = teams.get(element["team"], {})
            position_info = positions.get(element["element_type"], {})

            squad_players.append({
                "id": element["id"],
                "web_name": element.get("web_name"),
                "team": team_info.get("name", "Unknown"),
                "team_id": element.get("team"),
                "position": position_info.get("singular_name_short", "N/A"),
                "position_id": element.get("element_type"),
                "price": element.get("now_cost", 0) / 10,
                "predicted_score": _generate_predictions(element['id']),
            })

        team_counts = Counter(p["team_id"] for p in squad_players)

        candidate_pool = []
        squad_ids = {p["id"] for p in squad_players}
        for element in elements.values():
            team_info = teams.get(element["team"], {})
            position_info = positions.get(element["element_type"], {})
            candidate_pool.append({
                "id": element["id"],
                "web_name": element.get("web_name"),
                "team": team_info.get("name", "Unknown"),
                "team_id": element.get("team"),
                "position": position_info.get("singular_name_short", "N/A"),
                "position_id": element.get("element_type"),
                "price": element.get("now_cost", 0) / 10,
                "predicted_score": _generate_predictions(element['id']),
                "in_squad": element["id"] in squad_ids,
            })

        recommended_transfers = []
        for out_player in squad_players:
            best_option = None
            for candidate in candidate_pool:
                if candidate["id"] == out_player["id"]:
                    continue
                if candidate["in_squad"]:
                    continue
                if candidate["position_id"] != out_player["position_id"]:
                    continue
                if candidate["price"] > out_player["price"] + budget:
                    continue

                projected_team_count = team_counts[candidate["team_id"]]
                if candidate["team_id"] != out_player["team_id"]:
                    projected_team_count += 1
                if projected_team_count > team_limit:
                    continue

                gain = round(
                    candidate["predicted_score"] - out_player["predicted_score"]
                )
                if gain <= 0:
                    continue

                option = {
                    "out_player": out_player,
                    "in_player": candidate,
                    "expected_gain": gain,
                }
                if not best_option or gain > best_option["expected_gain"]:
                    best_option = option

            if best_option:
                recommended_transfers.append(best_option)

        recommended_transfers.sort(key=lambda t: t["expected_gain"], reverse=True)
        recommended_transfers = recommended_transfers[:5]

        top_predicted_players = sorted(
            [p for p in candidate_pool if not p["in_squad"]],
            key=lambda p: p["predicted_score"],
            reverse=True,
        )[:5]

        def build_strategy(name, transfer_limit_label, max_transfers):
            selected = recommended_transfers[:max_transfers]
            plan = []
            for idx, rec in enumerate(selected):
                plan.append({
                    "gameweek": current_event.get("id", 0) + idx,
                    "out_player": rec["out_player"],
                    "in_player": rec["in_player"],
                    "expected_gain": rec["expected_gain"],
                })
            expected_points = round(sum(step["expected_gain"] for step in plan))
            return {
                "name": name,
                "transfer_limit": transfer_limit_label,
                "expected_points": expected_points,
                "plan": plan,
            }

        safe_count = min(len(recommended_transfers), max(1, free_transfers))
        moderate_cap = min(len(recommended_transfers), free_transfers + 2, 5)
        moderate_count = max(1, moderate_cap)
        risky_count = min(len(recommended_transfers), 5) or 0

        strategies = []
        if recommended_transfers:
            strategies = [
                build_strategy("Safe", "No paid transfers", safe_count),
                build_strategy("Moderate", "Under 3 paid transfers", moderate_count),
                build_strategy("Risky", "Unlimited free transfers", risky_count),
            ]

        context.update({
            "recommended_transfers": recommended_transfers,
            "strategies": strategies,
            "top_predicted_players": top_predicted_players,
            "budget": budget,
            "free_transfers": free_transfers,
        })
    except Exception as exc:  # noqa: BLE001
        context["error_message"] = f"Could not build transfer suggestions: {exc}"

    return render(request, "fantasy/transfers.html", context)


@login_required
def gameweeks(request):
    gws = list(Gameweek.objects.order_by("fpl_id"))
    # find current index
    current_idx = next((i for i, gw in enumerate(gws) if gw.is_current), None)

    if current_idx is not None:
        gws = gws[current_idx:] + gws[:current_idx]

    return render(request, "fantasy/gameweeks.html", {"gameweeks": gws})


@login_required
def gameweek_details(request, gameweek_number):
    # Load gameweek from DB
    gameweek = get_object_or_404(Gameweek, fpl_id=gameweek_number)

    # Fetch fixtures from FPL API
    fixtures_url = f"https://fantasy.premierleague.com/api/fixtures/?event={gameweek.fpl_id}"
    response = requests.get(fixtures_url)
    fixtures_data = response.json()

    # Map team IDs to names (from DB)
    teams = {team.fpl_id: team.name for team in Team.objects.all()}

    fixtures = []
    for fixture in fixtures_data:
        fixtures.append({
            "home_team": teams.get(fixture["team_h"], "Unknown"),
            "away_team": teams.get(fixture["team_a"], "Unknown"),
            "kickoff_time": fixture["kickoff_time"],
            "finished": fixture["finished"],
            "home_score": fixture["team_h_score"],
            "away_score": fixture["team_a_score"],
            "home_team_code": fixture["team_h"],
            "away_team_code": fixture["team_a"],
        })

    return render(
        request,
        "fantasy/gameweek_details.html",
        {
            "gameweek": gameweek,
            "fixtures": fixtures,
        }
    )


# List of all teams with search
def teams(request):
    teams = Team.objects.all().order_by("-strength")

    return render(request, "fantasy/teams.html", {
        "teams": teams,
    })


@login_required
def team_details(request, team_id):
    STATUS_LABELS = {
        "a": "Active",
        "i": "Injured",
        "u": "Unavailable",
        "d": "Doubtful",
        "n": "Not in squad",
    }
    
    team = Team.objects.get(fpl_id=team_id)
    players = list(team.player_set.all())

    # Sort players: Active → Injured → Unavailable
    status_order = {"a": 0, "d": 1, "i": 2, "u": 3, "n": 4}
    players.sort(key=lambda p: status_order.get(p.status, 3))

    for player in players:
        player.predicted_score = _generate_predictions(player.fpl_id)

    # Add readable status attribute
    for p in players:
        p.status_display = STATUS_LABELS.get(p.status, p.status)

    return render(request, 'fantasy/team_details.html', {
        'team': team,
        'players': players,
        'positions': Position.objects.all()
    })


def update_fpl(request, token):
    if token != settings.FPL_CRON_TOKEN:  # check secret token
        return HttpResponseForbidden("Invalid token")
    call_command("update_fpl_data")
    return HttpResponse("FPL data updated")