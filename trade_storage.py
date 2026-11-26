import json
from pathlib import Path

TRADES_FILE = Path(__file__).with_name("trades.json")


def load_trades():
    if not TRADES_FILE.exists():
        return []
    with TRADES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_trades(trades):
    temp_file = TRADES_FILE.with_suffix(".tmp")
    with temp_file.open("w", encoding="utf-8") as file:
        json.dump(trades, file, indent=4)
    temp_file.replace(TRADES_FILE)