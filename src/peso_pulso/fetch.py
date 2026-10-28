"""Descargas verificadas contra el manifiesto del corte."""
from datetime import datetime, timezone
from pathlib import Path
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .io import config, digest, write_json


def fetch(root: Path, offline: bool = False) -> None:
    settings = config(root)
    session = requests.Session()
    session.headers["User-Agent"] = "PesoPulso/1.0 research-data-pipeline"
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    records = []
    for source in settings["sources"]:
        path = root / "data/raw" / source["file"]
        if not path.exists():
            if offline:
                raise FileNotFoundError(f"No existe {path.name}. Ejecute fetch con acceso a la red.")
            response = session.get(source["url"], timeout=(15, 120))
            response.raise_for_status()
            content = response.content
            if path.suffix == ".xlsx" and not content.startswith(b"PK"):
                raise ValueError(f"La respuesta de {path.name} no es un archivo XLSX.")
            if path.suffix == ".xls" and not content.startswith(bytes.fromhex("d0cf11e0")):
                raise ValueError(f"La respuesta de {path.name} no es un archivo XLS.")
            if path.suffix == ".json":
                json.loads(content)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".part")
            temporary.write_bytes(content)
            if digest(temporary) != source["sha256"]:
                temporary.unlink()
                raise ValueError(f"{path.name}: el proveedor cambió el archivo. Se conserva el corte anterior; revise la nueva versión y actualice config/sources.json explícitamente.")
            temporary.replace(path)
        if digest(path) != source["sha256"]:
            raise ValueError(f"Hash inesperado en {path.name}.")
        records.append({**source, "verified_at_utc": datetime.now(timezone.utc).isoformat()})
    write_json(root / "data/processed/source_manifest.json", {"snapshot_date": settings["snapshot_date"], "sources": records})
