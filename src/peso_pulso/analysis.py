"""Estadística descriptiva y asociación temporal con errores HAC."""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller
from .io import read_frame, write_frame, write_json


def lagged_pairs(frame: pd.DataFrame, outcome: str, lag: int) -> pd.DataFrame:
    return pd.DataFrame({"date":frame.date,"x":frame.trm_yoy_pct.shift(lag),"y":frame[outcome]}).dropna()


def analyze(root: Path) -> None:
    full = read_frame(root,"monthly")
    monthly = full[full.is_main_sample==1].copy()
    quarterly = read_frame(root,"quarterly")
    quarterly = quarterly[quarterly.is_main_sample==1].copy()
    rows = []
    for outcome in ["inflation_yoy_pct","exports_yoy_pct","imports_yoy_pct","brent_yoy_pct"]:
        for lag in [0,1,3,6,12]:
            pairs = lagged_pairs(full,outcome,lag)
            pairs = pairs[pairs.date.between("2015-01-01","2025-12-01")]
            for sample in ["2015–2025","Sin 2020–2021"]:
                selected = pairs if sample=="2015–2025" else pairs[~pairs.date.dt.year.isin([2020,2021])]
                rows.append({"outcome":outcome,"fx_lag_months":lag,"sample":sample,"n":len(selected),"pearson_r":selected.x.corr(selected.y),"spearman_r":selected.x.corr(selected.y,method="spearman")})
    correlations = pd.DataFrame(rows)
    write_frame(root/"reports/correlations.csv",correlations)
    qrows = []
    for x,y in [("trm_yoy_pct","gdp_yoy_pct"),("trm_qoq_pct","gdp_qoq_sa_pct")]:
        for sample in ["2015–2025","Sin 2020–2021"]:
            selected = quarterly if sample=="2015–2025" else quarterly[~quarterly.year.isin([2020,2021])]
            qrows.append({"x":x,"y":y,"sample":sample,"n":len(selected),"pearson_r":selected[x].corr(selected[y]),"spearman_r":selected[x].corr(selected[y],method="spearman")})
    write_frame(root/"reports/gdp_correlations.csv",pd.DataFrame(qrows))
    regime = monthly.groupby("regime",as_index=False).agg(months=("date","size"),mean_inflation_yoy_pct=("inflation_yoy_pct","mean"),mean_exports_yoy_pct=("exports_yoy_pct","mean"),mean_imports_yoy_pct=("imports_yoy_pct","mean"))
    write_frame(root/"reports/regime_summary.csv",regime)
    annual = full.groupby("year",as_index=False).agg(months=("date","size"),fx_days=("fx_days","sum"),exports_usd_m=("exports_usd_m","sum"),imports_usd_m=("imports_usd_m","sum"),brent_usd_bbl=("brent_usd_bbl","mean"))
    weights = full.assign(fx_weighted=full.trm_cop_usd*full.fx_days).groupby("year").fx_weighted.sum()
    annual["trm_cop_usd"] = annual.year.map(weights)/annual.fx_days
    annual["trade_balance_usd_m"] = annual.exports_usd_m-annual.imports_usd_m
    annual["trm_annual_avg_change_pct"] = annual.trm_cop_usd.pct_change(fill_method=None)*100
    december = full[full.month==12].set_index("year").inflation_yoy_pct
    annual["inflation_dec_pct"] = annual.year.map(december)
    gdp_all = read_frame(root,"quarterly")
    yearly_gdp = gdp_all.groupby("year").agg(gdp_real=("gdp_real_original","sum"),quarters=("quarter","size"))
    yearly_gdp = yearly_gdp[yearly_gdp.quarters==4]
    yearly_gdp["gdp_growth_pct"] = yearly_gdp.gdp_real.pct_change(fill_method=None)*100
    annual["gdp_growth_pct"] = annual.year.map(yearly_gdp.gdp_growth_pct)
    annual = annual[(annual.year>=2015)&(annual.year<=2025)&(annual.months==12)].copy()
    write_frame(root/"reports/annual.csv",annual)
    # Los rezagos se forman antes de recortar la muestra para conservar el historial.
    design = pd.DataFrame(index=full.index)
    for lag in [1,2,3]:
        design[f"fx_mom_lag{lag}"] = full.trm_mom_pct.shift(lag)
    design["brent_mom_lag1"] = full.brent_mom_pct.shift(1)
    design["inflation_mom_lag1"] = full.inflation_mom_pct.shift(1)
    design["pandemic"] = full.date.between("2020-03-01","2021-12-01").astype(float)
    months = pd.get_dummies(full.month,prefix="month",drop_first=True,dtype=float)
    design = pd.concat([design,months],axis=1)
    joined = pd.concat([full[["date","is_main_sample","inflation_mom_pct"]],design],axis=1).dropna()
    joined = joined[joined.is_main_sample==1]
    columns = list(design.columns)
    models, coefficients = {},[]
    for name, selected in [("full",joined)]:
        active_columns = [c for c in columns if selected[c].nunique()>1]
        x = sm.add_constant(selected[active_columns].astype(float))
        fit = sm.OLS(selected.inflation_mom_pct,x).fit(cov_type="HAC",cov_kwds={"maxlags":12})
        ci = fit.conf_int()
        for term in fit.params.index:
            coefficients.append({"model":name,"term":term,"coefficient":float(fit.params[term]),"std_error_hac":float(fit.bse[term]),"ci_lower_95":float(ci.loc[term,0]),"ci_upper_95":float(ci.loc[term,1]),"p_value":float(fit.pvalues[term]),"n":int(fit.nobs)})
        ljung = acorr_ljungbox(fit.resid,lags=[12],return_df=True)
        names = [f"fx_mom_lag{k}" for k in [1,2,3]]
        vector = np.array([1 if c in names else 0 for c in fit.params.index])
        effect = float(vector@fit.params)
        variance = max(float(vector@fit.cov_params()@vector),0)
        models[name] = {"n":int(fit.nobs),"r_squared":float(fit.rsquared),"adjusted_r_squared":float(fit.rsquared_adj),"hac_maxlags":12,"ljung_box_lag12_p":float(ljung.lb_pvalue.iloc[0]),"fx_lags_sum":effect,"fx_lags_sum_ci95":[effect-1.96*np.sqrt(variance),effect+1.96*np.sqrt(variance)],"interpretation":"Asociación acumulada entre los tres rezagos mensuales del dólar y la inflación mensual, en puntos porcentuales por 1% de variación cambiaria; no es un efecto causal.","observations":"Muestra mensual contigua; intervalos asintóticos normales. La sensibilidad sin 2020–2021 se limita a correlaciones descriptivas."}
    write_frame(root/"reports/model_coefficients.csv",pd.DataFrame(coefficients))
    diagnostics = []
    for name, values, deterministic in [("log_trm",np.log(monthly.trm_cop_usd),"ct"),("log_cpi",np.log(monthly.cpi_index),"ct"),("trm_mom_pct",monthly.trm_mom_pct,"c"),("inflation_mom_pct",monthly.inflation_mom_pct,"c")]:
        result = adfuller(values.dropna(),regression=deterministic,autolag="AIC",result_object=False)
        diagnostics.append({"series":name,"adf_statistic":float(result[0]),"p_value":float(result[1]),"lags":int(result[2]),"n":int(result[3]),"deterministic":deterministic})
    write_json(root/"reports/model_diagnostics.json",{"models":models,"adf":diagnostics,"limits":["Modelo asociativo; no identifica causalidad.","Variables omitidas: política monetaria, alimentos, regulados y condiciones globales.","La corrección HAC no elimina sesgo por endogeneidad ni garantiza estacionariedad.","Los valores p de correlaciones con muchos rezagos no se utilizan como descubrimientos confirmatorios."]})
    last = monthly.iloc[-1]
    year = annual.iloc[-1]
    contemporaneous = correlations[(correlations.fx_lag_months==0)&(correlations["sample"]=="2015–2025")]
    summary = {"snapshot_date":"2026-10-28","main_period":"2015–2025","months":len(monthly),"quarters":len(quarterly),"last_month":str(last.date.date()),"trm_dec_cop_usd":float(last.trm_cop_usd),"trm_dec_yoy_pct":float(last.trm_yoy_pct),"inflation_dec_yoy_pct":float(last.inflation_yoy_pct),"gdp_2025_growth_pct":float(year.gdp_growth_pct),"trade_balance_2025_usd_m":float(year.trade_balance_usd_m),"exports_2025_usd_m":float(year.exports_usd_m),"imports_2025_usd_m":float(year.imports_usd_m),"monthly_correlations":dict(zip(contemporaneous.outcome,contemporaneous.pearson_r.astype(float))),"gdp_yoy_correlation":qrows[0]["pearson_r"],"inflation_model":models["full"],"regimes":regime.to_dict(orient="records")}
    write_json(root/"reports/summary.json",summary)
    print(f"Análisis: {len(monthly)} meses, {len(quarterly)} trimestres; modelo HAC con {models['full']['n']} observaciones.")
