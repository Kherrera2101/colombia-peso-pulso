"""Entrada de ejecución del proyecto."""
import argparse
import os
from pathlib import Path
from .fetch import fetch
from .transform import build
from .analysis import analyze


def load_environment(root: Path) -> None:
    path=root/".env"
    allowed={"PGHOST","PGPORT","PGDATABASE","PGUSER","PGPASSWORD","POSTGRES_PASSWORD"}
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key,separator,value=line.partition("=")
            if separator and key.strip() in allowed:
                os.environ.setdefault(key.strip(),value.strip().strip("\"'"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Peso & Pulso | economía colombiana")
    parser.add_argument("command",choices=["fetch","build","analyze","render","powerbi","load","verify","all"])
    parser.add_argument("--root",type=Path,default=Path.cwd())
    parser.add_argument("--offline",action="store_true")
    parser.add_argument("--database",action="store_true",help="Incluye carga y conciliación PostgreSQL en all.")
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root/"config/sources.json").is_file():
        parser.error("Ejecute desde la raíz del repositorio o indique --root.")
    load_environment(root)
    try:
        if args.command in ["fetch","all"]:
            fetch(root,args.offline)
        if args.command in ["build","all"]:
            build(root)
        if args.command in ["analyze","all"]:
            analyze(root)
        if args.command in ["render","all"]:
            os.environ.setdefault("MPLCONFIGDIR",str(root/"data/local/matplotlib"))
            from .charts import render
            render(root)
        if args.command in ["powerbi","all"]:
            from .powerbi import create
            create(root)
        if args.command=="load" or (args.command=="all" and args.database):
            from .database import load
            load(root)
        if args.command=="verify" or (args.command=="all" and args.database):
            from .database import verify
            verify(root)
    except (ValueError,FileNotFoundError) as exc:
        parser.exit(1,f"Error: {exc}\n")


if __name__=="__main__":
    main()
