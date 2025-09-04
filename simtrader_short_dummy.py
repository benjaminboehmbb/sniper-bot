#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
simtrader_short_dummy.py
------------------------
Minimaler, stabiler Long/Short-Simulator auf Basis eines gewichteten Signal-Scores.
- Long-Entry:   score > +entry_th
- Short-Entry:  score < -entry_th
- Exit:         |score| <= exit_th  (Neutralzone), optional TP/SL
- Fees & Slippage berücksichtigt
- Ergebnisse: roi, num_trades, winrate, accuracy (+ getrennte Long/Short-Metriken)

Erwartete Inputs:
- DataFrame mit beliebigen Signalspalten; fehlende Spalten werden wie 0 behandelt.
- weights (Dict[str, float]): Spaltenname -> Gewicht
  Optionaler Modus in weights: "__mode__" in {"long","short","both"} (default "long")
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import math

import pandas as pd


@dataclass
class TradeState:
    side: Optional[str] = None        # "long", "short" oder None
    entry_price: float = 0.0
    pnl: float = 0.0
    wins: int = 0
    losses: int = 0
    trades_long: int = 0
    trades_short: int = 0
    pnl_long: float = 0.0
    pnl_short: float = 0.0


class SimTraderShortDummy:
    def __init__(self, df: pd.DataFrame, fees: float = 0.0005, slippage: float = 0.0002,
                 engine: str = "short_dummy", save_trades: bool = False,
                 entry_th: float = 0.5, exit_th: float = 0.05,
                 tp: float | None = None, sl: float | None = None) -> None:
        """
        :param df: Kurs-/Signal-DataFrame. Muss eine Preis-Spalte enthalten:
                   bevorzugt 'close' oder 'price' (Case-insensitiv).
        :param fees: Round-trip Gebühren (pro Trade beidseitig verrechnet)
        :param slippage: Round-trip Slippage
        :param entry_th: Eintrittsschwelle (Score)
        :param exit_th: Exit-Neutralzone (|score| <= exit_th => Exit)
        :param tp: optional Take Profit (z. B. 0.02 = 2%)
        :param sl: optional Stop Loss   (z. B. 0.01 = 1%)
        """
        self.df = df.copy()
        self.fees = float(fees)
        self.slippage = float(slippage)
        self.save_trades = bool(save_trades)
        self.entry_th = float(entry_th)
        self.exit_th = float(exit_th)
        self.tp = tp
        self.sl = sl

        # Preis-Spalte erkennen
        low_cols = {c.lower(): c for c in self.df.columns}
        price_col = None
        for cand in ("close", "price", "last", "close_price"):
            if cand in low_cols:
                price_col = low_cols[cand]
                break
        if price_col is None:
            # fallback: erste numerische Spalte nehmen
            for c in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[c]):
                    price_col = c
                    break
        if price_col is None:
            raise ValueError("Keine Preis-Spalte gefunden (erwartet z. B. 'close').")
        self.price_col = price_col

        # Trades loggen (optional)
        self._trades: list[dict[str, Any]] = []

    @staticmethod
    def _score(row: pd.Series, weights: Dict[str, float]) -> float:
        s = 0.0
        for k, w in weights.items():
            if k.startswith("__"):
                continue
            v = row.get(k, 0.0)
            try:
                s += float(w) * float(v)
            except Exception:
                # fehlende/unnütze Spalte => 0 Beitrag
                s += 0.0
        return float(s)

    def _enter(self, state: TradeState, side: str, price: float) -> None:
        state.side = side
        state.entry_price = price

    def _exit(self, state: TradeState, price: float) -> None:
        if state.side is None:
            return
        # Netto-Rendite pro Trade inkl. Fees+Slippage
        raw_ret = (price - state.entry_price) / state.entry_price if state.side == "long" else (state.entry_price - price) / state.entry_price
        net_ret = raw_ret - (self.fees + self.slippage)

        # Buchung
        if net_ret >= 0:
            state.wins += 1
        else:
            state.losses += 1

        if state.side == "long":
            state.trades_long += 1
            state.pnl_long += net_ret
        elif state.side == "short":
            state.trades_short += 1
            state.pnl_short += net_ret

        state.pnl += net_ret
        state.side = None
        state.entry_price = 0.0

    def run(self, weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Kompatible API:
        - analyze_unified.py ruft: metrics = trader.run(weights)
        - Optional in weights:
            "__mode__": "long" | "short" | "both" (default "long")
        """
        mode = str(weights.get("__mode__", "long")).lower()
        allow_long = mode in ("long", "both")
        allow_short = mode in ("short", "both")

        state = TradeState()

        for _, row in self.df.iterrows():
            price = float(row[self.price_col])
            score = self._score(row, weights)

            # Exit-Bedingungen (wenn Position offen)
            if state.side is not None:
                # TP/SL prüfen
                if self.tp is not None:
                    rr = (price - state.entry_price) / state.entry_price if state.side == "long" else (state.entry_price - price) / state.entry_price
                    if rr >= self.tp:
                        self._exit(state, price)
                        continue
                if self.sl is not None:
                    rr = (price - state.entry_price) / state.entry_price if state.side == "long" else (state.entry_price - price) / state.entry_price
                    if rr <= -self.sl:
                        self._exit(state, price)
                        continue

                # Neutralzone Exit (Score nahe 0)
                if abs(score) <= self.exit_th:
                    self._exit(state, price)
                    continue

                # Positionsflip erlauben: Wenn entgegengesetzte Entry-Schwelle stark überschritten ist
                if state.side == "long" and allow_short and score < -self.entry_th:
                    self._exit(state, price)
                    self._enter(state, "short", price)
                    continue
                if state.side == "short" and allow_long and score > self.entry_th:
                    self._exit(state, price)
                    self._enter(state, "long", price)
                    continue

            # Entry-Bedingungen (wenn keine Position offen)
            if state.side is None:
                if allow_long and score > self.entry_th:
                    self._enter(state, "long", price)
                    continue
                if allow_short and score < -self.entry_th:
                    self._enter(state, "short", price)
                    continue

        # Offene Position am Ende schließen
        if state.side is not None:
            self._exit(state, float(self.df[self.price_col].iloc[-1]))

        total_trades = state.trades_long + state.trades_short
        winrate = (state.wins / total_trades) if total_trades > 0 else 0.0
        accuracy = winrate  # hier synonym

        return {
            "roi": state.pnl,  # Summe der pro-Trade-Returns (approximierter ROI)
            "num_trades": total_trades,
            "winrate": winrate,
            "accuracy": accuracy,
            "roi_long": state.pnl_long,
            "roi_short": state.pnl_short,
            "num_trades_long": state.trades_long,
            "num_trades_short": state.trades_short,
        }
