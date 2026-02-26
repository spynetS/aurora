from __future__ import annotations

import json
import random

from rich import print as cprint
from aurora.functions import get_distro
from collections import Counter

from aurora.config.paths import important_updates_path, state_path
from aurora.main import package_count
from aurora.responses import (
    critical_severty,
    high_severity,
    low_severity,
    medium_severity,
)
from aurora.strings import CATEGORY_SUMMARY

RISK_ORDER = {
    "none":0,
    "low": 1,
    "medium": 2,
    "high": 4,
    "critical": 8,
}

COLORS = {
    "none": "white",
    "low": "green",
    "medium": "yellow",
    "high": "red",
    "critical": "dark_red",
}

distro = get_distro()
    
           

def get_risk_level(update_items: list[dict]) -> str:
    critical_present = False
    risk_sum = 0
    flagged_item_sum = 0
    for item in update_items:
        package_prefix = str(item).split("-")[0]
        
        if item in distro.FLAGGED_PACKAGES:
            item_risk = distro.FLAGGED_PACKAGES[item]["risk"]
        elif package_prefix in distro.FLAGGED_PACKAGES:
            item_risk = distro.FLAGGED_PACKAGES[package_prefix]["risk"]
        else:
            item_risk = "none"
        
        risk_sum = risk_sum + RISK_ORDER[item_risk]
    
    
    
    if risk_sum < 1:
        return "none"
    elif risk_sum < 4:
        return "low"
    elif risk_sum < 8:
        return "medium"
    elif risk_sum < 12:
        return "high"
    else:
        return "critical"


def get_cattegories(packages):
    categories = []
    for package in packages:
        package_prefix = str(package).split("-")[0]
        if package in distro.FLAGGED_PACKAGES:
            category = distro.FLAGGED_PACKAGES[package]["category"]
        elif package_prefix in distro.FLAGGED_PACKAGES:
            category = distro.FLAGGED_PACKAGES[package_prefix]["category"]
        else:
            category = "unknown"
        categories.append(category)
    return categories
    
def affected_areas(cattegories):
    counts = Counter(cattegories)
    
    print("Breakdown:")
    for item, count in counts.items():
        if item == "unknown":
            continue
        print(f"    {item}: ", end="")
        for _ in range(count):
            print("▉", end="")
        print(f" ({count})\n")

def summary(cattegories):
    counts = Counter(cattegories)

    array = []
    for item, count in counts.items():
        
        if item == "unknown":
            continue
        item_string = f"{count} {CATEGORY_SUMMARY[item].capitalize()}"
        array.append(item_string)
        
    output = ", ".join(array)
    
    print("Summary: ", end="")
    print(output, end=" pending\n")

def details(packages):
    by_risk = {"critical": [], "high": [], "medium": [], "low": []}

    for package in packages:
        package_prefix = str(package).split("-")[0]

        if package in distro.FLAGGED_PACKAGES:
            meta = distro.FLAGGED_PACKAGES[package]
        elif package_prefix in distro.FLAGGED_PACKAGES:
            meta = distro.FLAGGED_PACKAGES[package_prefix]
        else:
            meta = {"risk": "none", "category": "unknown"}

        risk = meta["risk"]
        category = meta["category"]

        if risk in by_risk:
            by_risk[risk].append({"name": package, "category": category})

    headers = {
        "critical": "Critical updates:",
        "high": "High-importance updates:",
        "medium": "Medium-importance updates:",
        "low": "Low-importance updates:",
    }
    print("Details:", end="\n   ")
    for risk in ["critical", "high", "medium", "low"]:
        items = by_risk[risk]
        if not items:
            continue
        print(headers[risk])
        for item in items:
            print(f"     - {item['name']} ({item['category']})")
    print()
        
                    
def main():
    with open(state_path, "r", encoding="utf-8") as f:
        upgradable_package_count = int(f.read().strip())
    
    with open("/tmp/update-list.txt", "r") as f:
        packages = []
        for line in f:
            package = line.strip()
            if not package:
                continue
            packages.append(package)
    risk_level = get_risk_level(packages)
    categories = get_cattegories(packages)
    
    if risk_level == "low":
        recommendation = random.choice(low_severity)
    elif risk_level == "medium":
        recommendation = random.choice(medium_severity)
    elif risk_level == "high":
        recommendation = random.choice(high_severity)
    else:  # critical
        recommendation = random.choice(critical_severty)
        
    color = COLORS[risk_level]
    
    # Output
    print("Aurora Status")
    print("─────────────")
    cprint(f"Severity: [{color}]{risk_level.upper()}[/{color}]")
    print(f"Updates: {upgradable_package_count} packages")
    summary(categories)
    print()
    
    affected_areas(categories)
    
    details(packages)
    
    
    print(f"Recomendation:")
    print(f"    {recommendation}")

if __name__ == "__main__":
   # aurora_status()
    main()
