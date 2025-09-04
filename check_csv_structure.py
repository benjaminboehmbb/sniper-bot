#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
check_csv_structure.py
---------------------------------
Intelligenter CSV-Checker für das sniper-bot-Projekt.

Funktionen:
- Erkennt Dateitypen: strategy, results, combined, aggregate, history, error, other
- Whitelistet bekannte Report-Dateien explizit (strategy_results.csv etc.)
- Prüft Pflichtspalten nur bei echten Eingabe- oder Ergebnis-Dateien
- Aggregat-/History-Dateien erzeugen keine unnötigen WARNs
- Übersichtlicher Konsolenreport + Logdatei mit Zeitstempel
"""

import csv
from pathlib import Path
from datetime import datetime

# === KONFIGURATION ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent

# Dateien, die bewusst ignoriert werden (z. B. sehr groß)
EXCLUDE_FILES = {"price_data_with_signals.csv", "price_data_with_signals.xlsx"}

# Harte Zuordnung bestimmter Dateinamen -> Typ
SPECIAL_NAME_TYPES = {
    "strategy_results.csv": "aggregate",
    "strategy_monthly_comparison.csv": "aggregate",
    "strategy_results_summary.csv": "aggregate",
    "strategy_comparison_extended.csv": "aggregate",
    "trade_history.csv": "history",
}

# Pflichtspalten pro Dateityp
MANDATORY_SETS = {
    "strategy": ["Combination"],                             # Strategielisten
    "results": ["roi", "num_trades", "winrate", "accuracy"], # Ergebnisse pro Strategie
    "combined": ["Combination", "roi"],                     # Kombinierte Dateien mit Zeitbezug
}
# =============================================================================


def detect_csv_type(file_path: Path, headers: list[str]) -> str:
    """
    Bestimmt Typ der CSV-Datei anhand von Name und Headern.
    """
    name = file_path.name.lower()
    headers_lower = [h.lower() for h in headers]
    parent_parts = [p.lower() for p in file_path.parent.parts]

    # 0) Harte Zuordnung
    if name in SPECIAL_NAME_TYPES:
        return SPECIAL_NAME_TYPES[name]

    # 1) Explizite Typen
    if "error" in name:
        return "error"
    if "trade_history" in name:
        return "history"
    if "results" in parent_parts or any(h in name for h in ("summary", "comparison", "monthly", "extended")):
        return "aggregate"
    if "results" in name or {"roi", "num_trades"} & set(headers_lower):
        return "results"
    if "combined" in name or "metrics" in name:
        return "combined"
    if "strategy" in name or "strategies" in name or "combination" in headers_lower:
        return "strategy"
    return "other"


def check_csv(file_path: Path):
    """
    Prüft eine CSV-Datei und gibt (Status, Liste von Meldungen) zurück.
    Status: OK, WARN, CRITICAL
    """
    try:
        with file_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers is None:
                return "CRITICAL", ["Leere Datei (keine Headerzeile)"]

            csv_type = detect_csv_type(file_path, headers)
            headers_lower = [h.lower() for h in headers]
            issues = []

            # Pflichtspalten prüfen
            if csv_type in MANDATORY_SETS:
                for col in MANDATORY_SETS[csv_type]:
                    if col.lower() not in headers_lower:
                        issues.append(f"Fehlende Spalte: {col}")

            # Zeitspalte prüfen bei strategy/combined
            if csv_type in ("strategy", "combined"):
                if not any(c in headers_lower for c in ["timestamp", "open_time"]):
                    issues.append("Keine Zeitspalte (timestamp/open_time)")

            # Zeilenanzahl prüfen (nur für relevante Typen)
            row_count = sum(1 for _ in reader)
            if row_count == 0 and csv_type not in ("aggregate", "history", "error"):
                issues.append("Keine Datenzeilen")

            if not issues:
                return "OK", []
            return ("CRITICAL", issues) if any("Header" in i or "Fehler" in i for i in issues) else ("WARN", issues)

    except Exception as e:
        return "CRITICAL", [f"Fehler beim Lesen: {e}"]


def scan_csv_files(root: Path):
    """
    Liefert alle relevanten CSV-Dateien rekursiv.
    """
    for p in root.rglob("*.csv"):
        if p.name in EXCLUDE_FILES:
            continue
        yield p


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = PROJECT_ROOT / f"csv_check_log_{timestamp}.txt"
    all_lines = []
    total = ok = warn = critical = 0

    print(f"🔍 CSV-Check (Projekt: {PROJECT_ROOT}) — {timestamp}\n")

    for csv_file in scan_csv_files(PROJECT_ROOT):
        total += 1
        rel = csv_file.relative_to(PROJECT_ROOT)
        status, issues = check_csv(csv_file)

        if status == "OK":
            ok += 1
            print(f"[OK] {rel}")
            all_lines.append(f"[OK] {rel}")
        elif status == "WARN":
            warn += 1
            for msg in issues:
                print(f"[WARN] {rel} -> {msg}")
                all_lines.append(f"[WARN] {rel} -> {msg}")
        else:
            critical += 1
            for msg in issues:
                print(f"[CRITICAL] {rel} -> {msg}")
                all_lines.append(f"[CRITICAL] {rel} -> {msg}")

    summary = [
        "\n=== Zusammenfassung ===",
        f"Gesamtdateien : {total}",
        f"OK           : {ok}",
        f"WARN         : {warn}",
        f"CRITICAL     : {critical}",
        f"Log-Datei    : {log_file.name}",
    ]
    print("\n".join(summary))
    all_lines.extend(summary)

    try:
        log_file.write_text("\n".join(all_lines), encoding="utf-8")
    except Exception as e:
        print(f"[WARN] Konnte Log nicht speichern: {e}")


if __name__ == "__main__":
    main()




