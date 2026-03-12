#!/usr/bin/env python3
import argparse
import json
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import requests


BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"


@dataclass
class BonusRule:
    """
    Represents a bonus free transfer rule for a specific gameweek.
    Due to AFCON, 5 transfers were granted ahead of GW 16.
    """
    event: int
    bonus: int
    cap_extra: int = 0


DEFAULT_BONUS_RULES: Dict[int, BonusRule] = {

    16: BonusRule(event=16, bonus=5, cap_extra=5),
}

DEFAULT_MAX_FREE_TRANSFERS = 5


def fetch_bootstrap() -> dict:
    resp = requests.get(BOOTSTRAP_URL, timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_entry_history(entry_id: int) -> dict:
    url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/history/"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_league_entries(league_id: int) -> List[int]:
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return [row["entry"] for row in data.get("standings", {}).get("results", [])]


def parse_bonus_rules(values: List[str]) -> Dict[int, BonusRule]:
    """
    Parse --bonus rules like: "18:5" or "18:5:5": event 18, +5 free transfers, +5 temporary cap extra (optional).
    """
    rules: Dict[int, BonusRule] = {}
    for raw in values:
        parts = raw.split(":")
        if len(parts) not in (2, 3):
            raise ValueError(f"Invalid bonus rule '{raw}'. Use EVENT:BONUS or EVENT:BONUS:CAP_EXTRA.")
        event = int(parts[0])
        bonus = int(parts[1])
        cap_extra = int(parts[2]) if len(parts) == 3 else 0
        rules[event] = BonusRule(event=event, bonus=bonus, cap_extra=cap_extra)
    return rules


def compute_free_transfers(history: dict, finished_event_ids: Iterable[int], base_cap: int, bonus_rules: Dict[int, BonusRule]) -> int:
    current = {row["event"]: row for row in history.get("current", [])}
    
    # Build chips lookup from the separate chips array
    chips_by_event: Dict[int, str] = {
        chip["event"]: chip["name"] for chip in history.get("chips", [])
    }
    
    # Start with 1 free transfer before GW1
    free_transfers = 1

    for event_id in finished_event_ids:
        # Check for bonus rules that apply BEFORE this gameweek's transfers
        bonus = 0
        bonus_cap_extra = 0
        
        if event_id in bonus_rules:
            rule = bonus_rules[event_id]
            bonus = rule.bonus
            bonus_cap_extra = rule.cap_extra
        
        # Apply bonus transfers and temporary cap increase
        cap_for_event = base_cap + bonus_cap_extra
        free_transfers = min(free_transfers + bonus, cap_for_event)

        # Get this gameweek's data
        row = current.get(event_id, {})
        transfers_used = row.get("event_transfers", 0) or 0
        
        # Get chip from the chips lookup (NOT from the row)
        chip = chips_by_event.get(event_id)

        # Calculate remaining after using transfers this GW
        remaining = max(0, free_transfers - transfers_used)

        # Determine free transfers for NEXT gameweek
        if chip in ("freehit", "wildcard"):
            # Wildcard and Free Hit reset to 1 free transfer
            free_transfers = 1
        else:
            # Roll over unused + gain 1 for next GW, capped at base_cap
            free_transfers = min(base_cap, remaining + 1)

    return free_transfers


def load_entry_ids(args: argparse.Namespace) -> List[int]:
    entry_ids: List[int] = []

    if args.entries:
        entry_ids.extend(args.entries)

    if args.entries_file:
        with open(args.entries_file, "r", encoding="ascii") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entry_ids.append(int(line))

    if args.league_id:
        entry_ids.extend(fetch_league_entries(args.league_id))

    deduped = sorted(set(entry_ids))
    if not deduped:
        raise ValueError("No entry IDs provided. Use --entries, --entries-file, or --league-id.")
    return deduped


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate remaining free transfers for FPL entries.",)
    parser.add_argument("--entries", nargs="*", type=int, help="FPL entry IDs")
    parser.add_argument("--entries-file", help="Path to file with one entry ID per line")
    parser.add_argument("--league-id", type=int, help="Classic league ID to pull entry IDs from")
    parser.add_argument(
        "--bonus",
        action="append",
        default=[],
        help="Bonus rule EVENT:BONUS or EVENT:BONUS:CAP_EXTRA (e.g., 18:5:5)",
    )
    parser.add_argument("--output", choices=("table", "json"), default="table")
    args = parser.parse_args()

    bootstrap = fetch_bootstrap()
    game_settings = bootstrap.get("game_settings", {})
    # 25/26 season: max free transfers is 5 (max_extra = 4)
    max_extra = int(game_settings.get("max_extra_free_transfers", DEFAULT_MAX_FREE_TRANSFERS - 1))
    base_cap = 1 + max_extra

    finished_events = [
        event["id"] for event in bootstrap.get("events", []) if event.get("finished")
    ]
    finished_events.sort()

    bonus_rules = dict(DEFAULT_BONUS_RULES)
    bonus_rules.update(parse_bonus_rules(args.bonus))
    entry_ids = load_entry_ids(args)

    results = []
    for entry_id in entry_ids:
        history = fetch_entry_history(entry_id)
        free_transfers = compute_free_transfers(
            history=history,
            finished_event_ids=finished_events,
            base_cap=base_cap,
            bonus_rules=bonus_rules,
        )
        results.append({
            "entry_id": entry_id,
            "free_transfers": free_transfers,
        })

    if args.output == "json":
        print(json.dumps(results, indent=2))
        return 0

    width = max(len(str(r["entry_id"])) for r in results)
    print(f"{'Entry ID'.ljust(width)}  Free Transfers")
    print(f"{'-' * width}  --------------")
    for row in results:
        print(f"{str(row['entry_id']).ljust(width)}  {row['free_transfers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
