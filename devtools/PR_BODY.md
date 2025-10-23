# Pull Request: 12-Indicator-Snapshot (clean)

## Kurzfassung
- Sauberer Code-Snapshot für die **12-Indicator-Arbeit** (`feat/12-indicators-clean2`)
- Große Datendateien **nicht im Repo** → lokal im Archiv `sniper-data-archive_2025-10-23.tar.gz`
- Ziel: saubere Grundlage zum Testen auf der Workstation

## Änderungen
- `scripts/` und `tools/` wiederhergestellt
- `.gitignore` ergänzt (data/, out/, results/)
- `requirements.txt` erzeugt
- `devtools/tailscale_notes.txt` hinzugefügt

## Warum
- Vermeidet GitHub-Limits (>100 MB)
- Reproduzierbarer Setup-Schritt für Workstation
- Große Daten separat (S3 / LFS / USB)

## Test-Plan
1. Klonen: `git clone git@github.com:benjaminboehmbb/sniper-bot.git && cd sniper-bot`
2. Branch: `git checkout feat/12-indicators-clean2`
3. Venv: `python -m venv .venv && source .venv/Scripts/activate`
4. Install: `pip install -r requirements.txt`
5. Smoke-Tests:  
   `python -m scripts.generate_combinations_universal --help`  
   `python -m tools.validate_price_1min --help`

