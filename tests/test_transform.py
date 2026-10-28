import pandas as pd
import pytest
from peso_pulso.transform import expand_trm, validate_series


def record(start,end,value):
    return {"vigenciadesde":start,"vigenciahasta":end,"valor":str(value),"unidad":"COP"}


def test_trm_weekend_uses_all_calendar_days():
    frame=expand_trm([record("2025-01-01","2025-01-01",4000),record("2025-01-02","2025-01-04",4200)])
    assert len(frame)==4
    assert frame.trm_cop_usd.mean()==4150
    assert frame.date.iloc[-1]==pd.Timestamp("2025-01-04")


def test_overlapping_validity_intervals_are_rejected():
    with pytest.raises(ValueError,match="superpuestas"):
        expand_trm([record("2025-01-01","2025-01-03",4000),record("2025-01-03","2025-01-04",4200)])


def test_trm_unit_is_checked():
    row=record("2025-01-01","2025-01-01",4000)
    row["unidad"]="USD"
    with pytest.raises(ValueError,match="Unidad"):
        expand_trm([row])


def test_missing_month_is_rejected():
    frame=pd.DataFrame({"date":pd.to_datetime(["2025-01-01","2025-03-01"]),"value":[1.,2.]})
    with pytest.raises(ValueError,match="huecos"):
        validate_series(frame,"MS",["value"])


def test_missing_value_is_rejected():
    frame=pd.DataFrame({"date":pd.date_range("2025-01-01",periods=3,freq="MS"),"value":[1.,None,3.]})
    with pytest.raises(ValueError,match="faltantes"):
        validate_series(frame,"MS",["value"])
