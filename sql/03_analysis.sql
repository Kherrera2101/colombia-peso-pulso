-- Asociación contemporánea: variaciones interanuales, muestra mensual.
SELECT count(*) AS months,
       corr(trm_yoy_pct,inflation_yoy_pct) AS r_fx_inflation,
       corr(trm_yoy_pct,exports_yoy_pct) AS r_fx_exports,
       corr(trm_yoy_pct,imports_yoy_pct) AS r_fx_imports,
       corr(trm_yoy_pct,brent_yoy_pct) AS r_fx_brent
FROM pp_mart.monthly_main;

-- El rezago se calcula sobre todo el historial antes de restringir la muestra.
WITH lagged AS (
    SELECT date,inflation_yoy_pct,
           lag(trm_yoy_pct,3) OVER (ORDER BY date) AS fx_lag3
    FROM pp_mart.monthly
)
SELECT count(fx_lag3) AS pairs,corr(fx_lag3,inflation_yoy_pct) AS r_fx_lag3_inflation
FROM lagged CROSS JOIN pp_core.study_config s
WHERE date BETWEEN s.sample_start AND s.sample_end;

-- Cambios anuales por régimen cambiario: comparación descriptiva.
SELECT * FROM pp_mart.regime_summary ORDER BY regime;

-- Crecimiento real y variación del dólar, conservando la frecuencia trimestral.
SELECT count(*) AS quarters,
       corr(trm_yoy_pct,gdp_yoy_pct) AS r_annual,
       corr(trm_qoq_pct,gdp_qoq_sa_pct) AS r_quarterly
FROM pp_mart.quarterly_main;

-- Sensibilidad a las observaciones de pandemia y recuperación.
SELECT corr(trm_yoy_pct,gdp_yoy_pct) AS r_without_2020_2021,count(*) AS quarters
FROM pp_mart.quarterly_main WHERE year NOT IN (2020,2021);

-- Balanza de bienes: ambas corrientes en millones de dólares FOB.
SELECT year,exports_usd_m,imports_usd_m,trade_balance_usd_m,
       sum(trade_balance_usd_m) OVER (ORDER BY year) AS cumulative_balance_usd_m
FROM pp_mart.annual ORDER BY year;

-- Volatilidad mensual de la variación diaria de la TRM, en porcentaje.
WITH returns AS (
    SELECT date,100*(ln(trm_cop_usd)-ln(lag(trm_cop_usd) OVER (ORDER BY date))) AS log_return
    FROM pp_core.trm_daily
)
SELECT date_trunc('month',date)::date AS month,stddev_samp(log_return) AS daily_volatility_pct
FROM returns GROUP BY 1 ORDER BY 1;
