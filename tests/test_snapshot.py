from pathlib import Path
import json
import numpy as np
import pandas as pd
from peso_pulso.io import read_frame
from peso_pulso.analysis import lagged_pairs

ROOT=Path(__file__).resolve().parents[1]


def test_main_sample_coverage_and_trade_identity():
    frame=read_frame(ROOT,"monthly")
    main=frame[frame.is_main_sample==1]
    assert len(main)==132
    assert (main.is_complete==1).all()
    assert np.allclose(main.exports_usd_m-main.imports_usd_m,main.trade_balance_usd_m)
    assert main.date.min()==pd.Timestamp("2015-01-01")
    assert main.date.max()==pd.Timestamp("2025-12-01")


def test_gdp_uses_original_for_yoy_and_adjusted_for_qoq():
    frame=read_frame(ROOT,"quarterly")
    assert len(frame.query("is_main_sample == 1"))==44
    assert np.allclose(frame.gdp_real_original.pct_change(4).iloc[4:]*100,frame.gdp_yoy_pct.iloc[4:])
    assert np.allclose(frame.gdp_real_sa.pct_change().iloc[1:]*100,frame.gdp_qoq_sa_pct.iloc[1:])


def test_lag_pairs_do_not_use_future_fx_values():
    frame=pd.DataFrame({"date":pd.date_range("2020-01-01",periods=4,freq="MS"),"trm_yoy_pct":[10.,20.,30.,40.],"outcome":[1.,2.,3.,4.]})
    pairs=lagged_pairs(frame,"outcome",1)
    assert pairs.iloc[0].x==10
    assert pairs.iloc[0].y==2
    assert pairs.iloc[-1].x==30


def test_summary_matches_versioned_data():
    summary=json.loads((ROOT/"reports/summary.json").read_text(encoding="utf-8"))
    m=read_frame(ROOT,"monthly").query("is_main_sample == 1")
    assert np.isclose(summary["monthly_correlations"]["inflation_yoy_pct"],m.trm_yoy_pct.corr(m.inflation_yoy_pct))
    assert np.isclose(summary["trm_dec_cop_usd"],m.iloc[-1].trm_cop_usd)
    assert summary["inflation_model"]["n"]==132


def test_powerbi_has_shared_date_dimension_and_no_embedded_credentials():
    path=ROOT/"powerbi/PesoPulso.SemanticModel/model.bim"
    doc=json.loads(path.read_text(encoding="utf-8"))
    model=doc["model"]
    assert {t["name"] for t in model["tables"]}=={"Calendar","Monthly","Quarterly"}
    assert len(model["relationships"])==2
    assert all(r["toTable"]=="Calendar" and r["toCardinality"]=="one" for r in model["relationships"])
    assert "password" not in path.read_text(encoding="utf-8").lower()
