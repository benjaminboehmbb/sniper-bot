# WORKSTATION REMOTE COMPUTE — OPERATIONS V1

- **Einrichtungsdatum:** 2026-08-07
- **Workstation:** `workstation`
- **Workstation-Tailscale-IP:** `100.125.59.14`
- **Laptop-Tailscale-IP:** `100.93.95.76`
- **Zugriffsweg:** Tailscale + Windows OpenSSH + WSL2 Ubuntu

## Betriebszustand

- Tailscale startet auf Laptop und Workstation automatisch.
- Tailscale läuft auf beiden Geräten im unbeaufsichtigten Modus und erhält
  automatische Updates.
- Windows OpenSSH (`sshd`) startet auf der Workstation automatisch.
- Der Netzbetrieb der Workstation ist auf keinen automatischen Standby und
  keinen automatischen Ruhezustand eingestellt.
- WSL2 Ubuntu verwendet `systemd` und den Benutzer `workstation`.
- Es ist keine Router-Portfreigabe erforderlich.

Die Workstation muss eingeschaltet, mit Strom versorgt und mit dem Internet
verbunden sein. Der Bildschirm darf ausgeschaltet und Windows darf gesperrt
sein. Bei ausgeschalteter Workstation ist kein Fernzugriff möglich.

## Täglicher Zugriff

Im Laptop-WSL genügt:

```bash
ssh workstation
```

Dieser Befehl öffnet direkt:

```text
/home/workstation/projects/sniper-bot
```

Die Sitzung läuft bereits im Workstation-WSL als Benutzer `workstation`.
Beenden mit:

```bash
exit
```

Nach einem Laptop-/WSL-Neustart kann beim ersten Zugriff einmal die
Passphrase des SSH-Schlüssels abgefragt werden. Danach hält der automatisch
gestartete SSH-Agent den Schlüssel für weitere Zugriffe bereit.

Für technische Windows-Automation existiert getrennt der Alias:

```bash
ssh workstation-win
```

## Feste Verzeichnisstruktur auf der Workstation

| Zweck | Pfad |
|---|---|
| Projektcode | `/home/workstation/projects/sniper-bot` |
| Große Datensätze | `/home/workstation/datasets/sniper-bot` |
| Rechenläufe und Belege | `/home/workstation/runs/sniper-bot` |
| Kurzfristige Übertragungen | `/home/workstation/transfers` |

Große Datensätze und reproduzierbare Rohlogs werden nicht in Git gespeichert.
Manifeste, Hashes, Sidecar-Berichte und entscheidungsrelevante Belege werden
dokumentiert und bei Bedarf in das Laptop-Projekt übernommen.

## Verbindlicher Arbeitsablauf

1. Änderungen werden auf einem separaten Git-Branch vorbereitet und getestet.
2. Nur ein sauberer, identifizierter Commit wird auf die Workstation übertragen.
3. Lange Rechenläufe starten ausschließlich auf der Workstation.
4. Jeder Lauf bindet Code, Profil, Seed und Datensatz per Commit bzw. SHA-256.
5. Ergebnisse werden geprüft; kleine Belege bleiben erhalten, große
   reproduzierbare Zwischenprodukte werden nach Hash-Dokumentation entfernt.
6. Kein IU-4- oder Live-Schritt erfolgt ohne ausdrückliche Freigabe.

## Aktueller geprüfter Stand

- **Workstation-Projekt-Commit:**
  `ab060bd50670786a228b69418b96c9a580313d9a`
- **Workstation-Projektstatus:** sauber
- **SSH über Tailscale:** erfolgreich geprüft
- **Direkte WSL-/Projektlandung:** erfolgreich geprüft
