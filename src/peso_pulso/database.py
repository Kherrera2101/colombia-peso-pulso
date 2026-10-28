"""Carga transaccional y conciliación independiente SQL/Python."""
from pathlib import Path
import json
import os
import uuid
import numpy as np
import pandas as pd
import psycopg
from psycopg import sql
from .io import config, read_frame, write_json, digest


def connection():
    return psycopg.connect(host=os.getenv("PGHOST","127.0.0.1"),port=os.getenv("PGPORT","5433"),dbname=os.getenv("PGDATABASE","peso_pulso"),user=os.getenv("PGUSER","peso_pulso"),password=os.getenv("PGPASSWORD") or os.getenv("POSTGRES_PASSWORD",""),connect_timeout=10)


def copy_frame(cursor, table: str, frame: pd.DataFrame) -> None:
    schema,name = table.split(".")
    statement = sql.SQL("COPY {}.{} ({}) FROM STDIN").format(sql.Identifier(schema),sql.Identifier(name),sql.SQL(",").join(map(sql.Identifier,frame.columns)))
    with cursor.copy(statement) as stream:
        for row in frame.itertuples(index=False,name=None):
            clean = tuple(None if pd.isna(value) else value.to_pydatetime().date() if isinstance(value,pd.Timestamp) else value.item() if isinstance(value,np.generic) else value for value in row)
            stream.write_row(clean)


def load(root: Path) -> None:
    settings = config(root)
    with connection() as conn,conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(hashtext('peso_pulso_load'))")
        cur.execute((root/"sql/01_schema.sql").read_text(encoding="utf-8"))
        cur.execute("TRUNCATE pp_core.trm_daily,pp_core.brent_daily,pp_core.monthly_base,pp_core.quarterly_base,pp_core.calendar,pp_core.study_config,pp_raw.fx_interval,pp_raw.source_file")
        for source in settings["sources"]:
            path = root/"data/raw"/source["file"]
            if path.exists() and digest(path)!=source["sha256"]:
                raise ValueError(f"Hash inválido: {source['file']}")
            payload = path.read_bytes() if path.exists() else None
            cur.execute("INSERT INTO pp_raw.source_file (source_id,filename,publisher,source_url,terms_url,sha256,snapshot_date,payload) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(source["id"],source["file"],source["entity"],source["url"],source["terms"],source["sha256"],settings["snapshot_date"],payload))
        trm_file = root/"data/raw/trm.json"
        if trm_file.exists():
            records = json.loads(trm_file.read_text(encoding="utf-8"))
            intervals = pd.DataFrame([(pd.Timestamp(r["vigenciadesde"]),pd.Timestamp(r["vigenciahasta"]),float(r["valor"])) for r in records],columns=["valid_from","valid_to","trm_cop_usd"])
            copy_frame(cur,"pp_raw.fx_interval",intervals)
        cur.execute("INSERT INTO pp_core.study_config (sample_start,sample_end) VALUES (%s,%s)",(settings["sample_start"],settings["sample_end"]))
        for filename, table,columns in [
            ("calendar","pp_core.calendar",["date","year","month","month_label","quarter_label"]),
            ("trm_daily","pp_core.trm_daily",["date","trm_cop_usd"]),
            ("brent_daily","pp_core.brent_daily",["date","brent_usd_bbl"]),
            ("monthly","pp_core.monthly_base",["date","trm_cop_usd","fx_days","cpi_index","exports_usd_m","imports_usd_m","brent_usd_bbl","brent_days"]),
            ("quarterly","pp_core.quarterly_base",["date","gdp_real_original","gdp_real_sa","revision","trm_cop_usd","brent_usd_bbl","exports_usd_m","imports_usd_m"]),
        ]:
            copy_frame(cur,table,read_frame(root,filename)[columns])
        cur.execute((root/"sql/02_views.sql").read_text(encoding="utf-8"))
        counts = [len(read_frame(root,n)) for n in ["monthly","quarterly"]]
        cur.execute("INSERT INTO pp_core.pipeline_run (run_id,snapshot_date,monthly_rows,quarterly_rows) VALUES (%s,%s,%s,%s)",(uuid.uuid4(),settings["snapshot_date"],*counts))
    print("Carga PostgreSQL confirmada en una transacción.")


def verify(root: Path) -> None:
    results = {}
    with connection() as conn,conn.cursor() as cur:
        cur.execute("SELECT version()")
        results["server_version"] = cur.fetchone()[0].split(" on ")[0]
        for name,fields in [("monthly",["trm_cop_usd","inflation_yoy_pct","trm_yoy_pct","exports_yoy_pct","imports_yoy_pct","brent_yoy_pct","trade_balance_usd_m"]),("quarterly",["gdp_yoy_pct","gdp_qoq_sa_pct","trm_yoy_pct","trm_qoq_pct"])]:
            expected = read_frame(root,name)
            expected = expected[expected.is_main_sample==1].sort_values("date")
            statement = sql.SQL("SELECT date,{} FROM pp_mart.{} ORDER BY date").format(sql.SQL(",").join(map(sql.Identifier,fields)),sql.Identifier(name+"_main"))
            cur.execute(statement)
            actual = pd.DataFrame(cur.fetchall(),columns=["date",*fields])
            actual["date"] = pd.to_datetime(actual.date)
            if list(actual.date)!=list(expected.date):
                raise ValueError(f"Fechas inconsistentes en {name}.")
            if not np.allclose(actual[fields].to_numpy(dtype=float),expected[fields].to_numpy(dtype=float),rtol=1e-9,atol=1e-7,equal_nan=True):
                raise ValueError(f"La conciliación SQL/Python falló en {name}.")
            results[name] = {"rows":len(actual),"indicators_reconciled":len(fields),"max_absolute_error":float(np.max(np.abs(actual[fields].to_numpy(dtype=float)-expected[fields].to_numpy(dtype=float))))}
        cur.execute("SELECT count(*) FROM pp_raw.source_file WHERE payload IS NOT NULL")
        results["source_files_archived"] = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM pp_raw.fx_interval")
        results["original_fx_intervals"] = cur.fetchone()[0]
        annual_expected=pd.read_csv(root/"reports/annual.csv")
        cur.execute("SELECT year,trm_cop_usd,exports_usd_m,imports_usd_m,trade_balance_usd_m,inflation_dec_pct,trm_annual_avg_change_pct FROM pp_mart.annual ORDER BY year")
        annual_actual=pd.DataFrame(cur.fetchall(),columns=["year","trm_cop_usd","exports_usd_m","imports_usd_m","trade_balance_usd_m","inflation_dec_pct","trm_annual_avg_change_pct"])
        fields=list(annual_actual.columns[1:])
        if list(annual_actual.year)!=list(annual_expected.year) or not np.allclose(annual_actual[fields].to_numpy(dtype=float),annual_expected[fields].to_numpy(dtype=float),atol=1e-7,rtol=1e-9):
            raise ValueError("La conciliación anual SQL/Python falló.")
        results["annual"]={"rows":len(annual_actual),"indicators_reconciled":len(fields)}
    results["status"] = "passed"
    write_json(root/"reports/database_validation.json",results)
    print("Conciliación PostgreSQL/Python superada.")
