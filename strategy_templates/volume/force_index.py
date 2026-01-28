"""Force Index and Ease of Movement"""
import pandas as pd
from typing import Dict
from ..base import Strategy, EPSILON
class EaseOfMovement(Strategy):
    def __init__(self, params: Dict):
        super().__init__("EaseOfMovement", params)
        self.period = params.get("period", 14)
        self.rules = [{"type": "entry_long", "condition": "EOM > 0"}, {"type": "entry_short", "condition": "EOM < 0"}]
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        if "high" in df.columns and "volume" in df.columns:
            dm = ((df["high"] + df["low"]) / 2) - ((df["high"].shift(1) + df["low"].shift(1)) / 2)
            br = df["volume"] / (df["high"] - df["low"] + EPSILON)
            eom = (dm / (br + EPSILON)).rolling(self.period).mean()
            signals[(eom > 0) & (eom.shift(1) <= 0)], signals[(eom < 0) & (eom.shift(1) >= 0)] = 1, -1
        return signals
