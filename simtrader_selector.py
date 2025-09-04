# simtrader_selector.py
from typing import Any
from importlib import import_module

def get_simtrader(engine: str = "default"):
    """
    Liefert eine SimTrader-Klasse je nach Engine-String.
    - "default"    -> simtrader.SimTrader         (dein aktueller Long-Trader)
    - "short_dummy"-> simtrader_short_dummy.SimTraderShortDummy
    """
    engine = (engine or "default").lower()
    if engine == "short_dummy":
        mod = import_module("simtrader_short_dummy")
        return getattr(mod, "SimTraderShortDummy")
    # fallback: dein bestehender Trader
    mod = import_module("simtrader")
    return getattr(mod, "SimTrader")
