#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backup-Skript für 'sniper-bot' (sicher parallel zum Deep-Dive nutzbar)

Funktionen:
- Sichert relevante Ergebnis- & CSV-Dateien mit Zeitstempel in Zielordner
- Hash-Check (MD5): kopiert nur, wenn Inhalt neu/anders ist (spart Speicher/Zeit)
- Dry-Run, Retention (Aufbewahrung der letzten N Backups), ausführliches Logging
- Fehlertolerant: schlägt nicht fehl, wenn Dateien gelockt sind – schreibt Warnung ins Log

Empfohlene Nutzung:
    python backup_project.py --dest "D:\\sniper-bot-backups"
    python backup_project.py --dest "D:\\sniper-bot-backups" --retention 10
    python backup_project.py --dest "D:\\sniper-bot-backups" --dry-run
"""

import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# === Konfiguration (bei Bedarf anpassen) =====================================

# Basis-Dateitypen/Patterns, die typischerweise sinnvoll sind zu sichern
FILE_PATTERNS = [
    # Ergebnis-CSV & Metriken
    "strategy_results*.csv",
    "combined*.csv",
    "metrics*.csv",
    "errors*.csv",
    "*_backup_*.csv",
    # Logs & JSON
    "*.log",
    "*.json",
    # ggf. Zusatzdaten
    "*.parquet",
]

# Verzeichnis-Patterns, in denen typischerweise Ergebnisse liegen:
DIR_PATTERNS_TO_SCAN = [
    "deep_out_*",
    "out_*",
    # in *_clean-Ordnern nur Unterordner mit Ergebnissen
    "*_clean/*/strategy_analysis_output_*",
]

# Zusätzliche Einzeldateien im Projektwurzelordner, die wir häufig sichern wollen
TOP_LEVEL_FILES = [
    "strategy_results*.csv",     # Falls auf Root-Ebene vorhanden
    "price_data_with_signals.csv",  # Nur wenn gewünscht; ggf. auskommentieren wenn zu groß
    # "price_data_with_signals.xlsx", # optional – i. d. R. groß; nur bei Bedarf
    "project_structure.md",
]

# Ordner/Dateinamen, die wir immer ignorieren:
GLOBAL_EXCLUDES = {
    ".git", ".venv", "__pycache__", ".mypy_cache", ".pytest_cache",
}

# === Ende Konfiguration =======================================================


def md5sum(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """MD5-Hash einer Datei berechnen (chunked)."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def collect_candidates(project_root: Path) -> list[Path]:
    """Sammle alle zu sichernden Dateien gemäß Patterns & Verzeichnis-Scans."""
    found: set[Path] = set()

    # Top-Level-Dateien
    for patt in TOP_LEVEL_FILES:
        for p in project_root.glob(patt):
            if p.is_file():
                found.add(p)

    # Verzeichnis-Scans
    for dpat in DIR_PATTERNS_TO_SCAN:
        for d in project_root.glob(dpat):
            if not d.exists():
                continue
            if d.is_dir():
                # innerhalb dieses Ordners alle FILE_PATTERNS sammeln
                for fp in FILE_PATTERNS:
                    for p in d.rglob(fp):
                        if p.is_file():
                            found.add(p)
            elif d.is_file():
                # Falls Pattern auf Datei matcht (eher selten)
                found.add(d)

    # Zusätzlich: falls jemand Muster direkt im Root erwartet (z.B. metrics*.csv)
    for fp in FILE_PATTERNS:
        for p in project_root.glob(fp):
            if p.is_file():
                found.add(p)

    # Globale Excludes filtern
    filtered = []
    for p in found:
        # wenn einer der globalen Excludes im relativen Teilpfad vorkommt → skip
        rel_parts = set(p.relative_to(project_root).parts)
        if rel_parts & GLOBAL_EXCLUDES:
            continue
        filtered.append(p)

    # Stabile Reihenfolge
    return sorted(filtered, key=lambda x: str(x).lower())


def rotation_cleanup(dest_root: Path, retention: int):
    """Löscht ältere Backup-Verzeichnisse, behält nur die letzten 'retention'."""
    if retention <= 0:
        return
    backups = sorted(
        [p for p in dest_root.glob("backup_*") if p.is_dir()],
        key=lambda x: x.name
    )
    if len(backups) <= retention:
        return
    to_delete = backups[: len(backups) - retention]
    for d in to_delete:
        try:
            shutil.rmtree(d)
        except Exception as e:
            print(f"[WARN] Konnte alten Backup-Ordner nicht löschen: {d} ({e})")


def main():
    parser = argparse.ArgumentParser(description="Backup relevanter sniper-bot Dateien")
    parser.add_argument("--dest", required=True, help="Zielordner für Backups, z. B. D:\\sniper-bot-backups")
    parser.add_argument("--retention", type=int, default=0, help="Anzahl zu behaltender Backups (0 = keine Löschung)")
    parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, was passieren würde")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    dest_root = Path(args.dest).expanduser().resolve()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = dest_root / f"backup_{timestamp}"
    log_file = backup_dir / f"backup_log_{timestamp}.txt"

    # Vorbereitung
    ensure_dir(dest_root)
    if not args.dry_run:
        ensure_dir(backup_dir)

    # Retention (vorneweg, damit wir Platz schaffen)
    rotation_cleanup(dest_root, args.retention)

    # Kandidaten sammeln
    candidates = collect_candidates(project_root)

    # Logging Header
    header = [
        f"# Backup gestartet: {datetime.now().isoformat(timespec='seconds')}",
        f"Projekt: {project_root}",
        f"Ziel:    {backup_dir if not args.dry_run else '(DRY-RUN) ' + str(backup_dir)}",
        f"Anzahl Kandidaten: {len(candidates)}",
        f"Retention: {args.retention}",
        "",
    ]
    print("\n".join(header))

    # Log vorbereiten
    log_lines = header.copy()

    copied = 0
    skipped = 0
    errored = 0

    for src in candidates:
        rel = src.relative_to(project_root)
        dst = (backup_dir / rel) if not args.dry_run else None
        line_prefix = f"[{rel}]"

        # Zielordner anlegen (außer Dry-Run)
        if dst and not args.dry_run:
            ensure_dir(dst.parent)

        try:
            action = "COPY"
            if not args.dry_run and dst.exists():
                # Wenn schon existiert: Hash vergleichen
                try:
                    if md5sum(src) == md5sum(dst):
                        action = "SKIP (identisch)"
                        skipped += 1
                        msg = f"{line_prefix} {action}"
                        print(msg)
                        log_lines.append(msg)
                        continue
                except Exception as he:
                    # Wenn Hash-Vergleich fehlschlägt, versuchen wir trotzdem zu kopieren
                    log_lines.append(f"{line_prefix} [WARN] Hash-Vergleich fehlgeschlagen: {he}; kopiere trotzdem")

            if args.dry_run:
                msg = f"{line_prefix} WOULD COPY -> {rel}"
            else:
                shutil.copy2(src, dst)
                msg = f"{line_prefix} COPIED -> {rel}"
                copied += 1

            print(msg)
            log_lines.append(msg)

        except Exception as e:
            errored += 1
            msg = f"{line_prefix} [ERROR] {e}"
            print(msg)
            log_lines.append(msg)

    summary = [
        "",
        "=== Zusammenfassung ===",
        f"Kopiert : {copied}",
        f"Überspr.: {skipped}",
        f"Fehler : {errored}",
        f"Log-Datei: {log_file if not args.dry_run else '(DRY-RUN) kein Log geschrieben'}",
    ]
    print("\n".join(summary))
    log_lines.extend(summary)

    # Log schreiben (nicht im Dry-Run)
    if not args.dry_run:
        try:
            ensure_dir(log_file.parent)
            log_file.write_text("\n".join(log_lines), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] Konnte Log nicht schreiben: {e}")


if __name__ == "__main__":
    # Windows stdout utf-8-safe
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
