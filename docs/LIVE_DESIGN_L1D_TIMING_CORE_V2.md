# LIVE DESIGN — L1-D TIMING CORE v2
Projekt: Sniper-Bot  
Phase: L1-D — 5m Timing Core v2  
Datum: 2026-01-20  
Status: DRAFT

---

## Ziel

Design-Dokument für den echten 5m Timing Core v2.

Noch keine Implementierung.
Noch kein Code.
Nur Architektur.



## Scope von Timing Core v2

Timing Core v2 ist ein reines **5m-Gate-Modul** mit folgenden Aufgaben:

- liest echte 5m-Kerzen (OHLCV)  
- wertet GS-Seeds auf 5m-Snapshots aus  
- liefert pro Tick genau ein Vote:

  - direction ∈ {long, short, none}  
  - strength ∈ [0,1]  

- wird von L1 pro Tick aufgerufen  
- löst **keine Execution** aus  

Nicht Teil von v2:

- keine Trades  
- keine Order-Logik  
- keine Positionslogik  
- keine Portfolio-Logik  
- keine Optimierung  
- kein Lernen  

Timing Core v2 ist ein **reines Bewertungs- und Gate-Modul**.


## Öffentliche API (Signatur v2)

Timing Core v2 stellt genau **eine öffentliche Funktion** bereit:

```python
TimingVote = compute_5m_timing_vote_v2(
    repo_root: str,
    symbol: str,
    now_utc: str,
    candles_5m: List[Candle5m],
    seeds: List[GSSpec],
    thresh: float,
)


## Datenstruktur: 5m-Kerze (Candle5m)

Timing Core v2 arbeitet ausschließlich mit bereits aggregierten 5m-Kerzen.

Struktur:

```python
class Candle5m:
    ts_open_utc: str      # ISO-UTC, Beginn der 5m-Kerze
    open: float
    high: float
    low: float
    close: float
    volume: float
