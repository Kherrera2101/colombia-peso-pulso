"""Configuración y persistencia del corte de datos."""
from pathlib import Path
import hashlib
import json
import pandas as pd


def config(root: Path) -> dict:
    return json.loads((root / "config/sources.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def write_frame(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, date_format="%Y-%m-%d", float_format="%.10f", encoding="utf-8", lineterminator="\n")


def read_frame(root: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(root / "data/processed" / f"{name}.csv", parse_dates=["date"])
