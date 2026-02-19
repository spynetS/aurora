from __future__ import annotations

import json
import random

from rich import print as cprint

from aurora.config.paths import important_updates_path, state_path
from aurora.main import package_count
from aurora.responses import (
    critical_severty,
    high_severity,
    low_severity,
    medium_severity,
)

RISK_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}

CATEGORY_RISK = {
    "kernel": "high",
    "boot": "high",
    "bootloader": "high",
    "core": "high",
    "core-lib": "critical",
    "package-manager": "high",
    "runtime": "low",
    "crypto": "medium",
    "trust": "medium",
}

COLORS = {
    "low": "white",
    "medium": "yellow",
    "high": "red",
    "critical": "dark_red",
}


def find_highest_risk(update_items: list[dict]) -> str:
    risk_levels: list[str] = []
    for item in update_items:
        risk = item.get("risk", "low")
        if risk not in risk_levels:
            risk_levels.append(risk)

    if not risk_levels:
        return "low"

    return max(risk_levels, key=lambda r: RISK_ORDER.get(r, 0))


def aurora_status() -> None:
    with open(important_updates_path, "r", encoding="utf-8") as f:
        update_data = json.load(f)

    with open(state_path, "r", encoding="utf-8") as f:
        upgradable_package_count = int(f.read().strip())

    important_updates = update_data.get("important_updates", [])

    package_count(upgradable_package_count)

    overall_risk = find_highest_risk(important_updates)
    print(f"Severity: {overall_risk}")

    affected_categories: list[str] = []
    for item in important_updates:
        category = item.get("category")
        if category and category not in affected_categories:
            affected_categories.append(category)

    print("Affected areas:")
    for category in affected_categories:
        category_risk = CATEGORY_RISK.get(category, "low")
        color = COLORS[category_risk]

        padded_category = f"{category:<{12}}"
        cprint(f"   [{color}]{padded_category}[/{color}]", end="")

        category_count = sum(
            1 for item in important_updates if item.get("category") == category
        )

        for _ in range(category_count):
            print("▉", end="")
        print(f" ({category_count})\n")

    if overall_risk == "low":
        recommendation = random.choice(low_severity)
    elif overall_risk == "medium":
        recommendation = random.choice(medium_severity)
    elif overall_risk == "high":
        recommendation = random.choice(high_severity)
    else:  # critical
        recommendation = random.choice(critical_severty)

    print(f"Recommendation: {recommendation}")


if __name__ == "__main__":
    aurora_status()
