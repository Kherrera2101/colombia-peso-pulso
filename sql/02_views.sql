CREATE OR REPLACE VIEW pp_mart.monthly AS
WITH changes AS (
    SELECT b.*,
           100 * (trm_cop_usd / nullif(lag(trm_cop_usd) OVER w,0)-1) AS trm_mom_pct,
           100 * (trm_cop_usd / nullif(lag(trm_cop_usd,12) OVER w,0)-1) AS trm_yoy_pct,
           100 * (cpi_index / nullif(lag(cpi_index) OVER w,0)-1) AS inflation_mom_pct,
           100 * (cpi_index / nullif(lag(cpi_index,12) OVER w,0)-1) AS inflation_yoy_pct,
           100 * (exports_usd_m / nullif(lag(exports_usd_m,12) OVER w,0)-1) AS exports_yoy_pct,
           100 * (imports_usd_m / nullif(lag(imports_usd_m,12) OVER w,0)-1) AS imports_yoy_pct,
           100 * (brent_usd_bbl / nullif(lag(brent_usd_bbl,12) OVER w,0)-1) AS brent_yoy_pct
    FROM pp_core.monthly_base b
    WINDOW w AS (ORDER BY date)
)
SELECT c.*, exports_usd_m-imports_usd_m AS trade_balance_usd_m,
       extract(year FROM date)::integer AS year,
       extract(month FROM date)::integer AS month,
       CASE WHEN trm_yoy_pct < 0 THEN 'Apreciación'
            WHEN trm_yoy_pct > 0 THEN 'Depreciación' ELSE 'Sin cambio' END AS regime,
       (exports_usd_m IS NOT NULL AND imports_usd_m IS NOT NULL AND brent_usd_bbl IS NOT NULL)::integer AS is_complete
FROM changes c;

CREATE OR REPLACE VIEW pp_mart.monthly_main AS
SELECT m.* FROM pp_mart.monthly m CROSS JOIN pp_core.study_config s
WHERE m.date BETWEEN s.sample_start AND s.sample_end;

CREATE OR REPLACE VIEW pp_mart.quarterly AS
SELECT b.*,
       100*(gdp_real_original/nullif(lag(gdp_real_original,4) OVER w,0)-1) AS gdp_yoy_pct,
       100*(gdp_real_sa/nullif(lag(gdp_real_sa) OVER w,0)-1) AS gdp_qoq_sa_pct,
       100*(trm_cop_usd/nullif(lag(trm_cop_usd,4) OVER w,0)-1) AS trm_yoy_pct,
       100*(trm_cop_usd/nullif(lag(trm_cop_usd) OVER w,0)-1) AS trm_qoq_pct,
       100*(brent_usd_bbl/nullif(lag(brent_usd_bbl,4) OVER w,0)-1) AS brent_yoy_pct,
       extract(year FROM date)::integer AS year,
       extract(quarter FROM date)::integer AS quarter
FROM pp_core.quarterly_base b
WINDOW w AS (ORDER BY date);

CREATE OR REPLACE VIEW pp_mart.quarterly_main AS
SELECT q.* FROM pp_mart.quarterly q CROSS JOIN pp_core.study_config s
WHERE q.date BETWEEN s.sample_start AND s.sample_end;

CREATE OR REPLACE VIEW pp_mart.calendar_main AS
SELECT c.* FROM pp_core.calendar c CROSS JOIN pp_core.study_config s
WHERE c.date >= s.sample_start AND c.date < s.sample_end + interval '1 month';

CREATE OR REPLACE VIEW pp_mart.regime_summary AS
SELECT regime,count(*) AS months,
       avg(inflation_yoy_pct) AS mean_inflation_yoy_pct,
       avg(exports_yoy_pct) AS mean_exports_yoy_pct,
       avg(imports_yoy_pct) AS mean_imports_yoy_pct
FROM pp_mart.monthly_main GROUP BY regime;

CREATE OR REPLACE VIEW pp_mart.annual AS
WITH totals AS (
    SELECT year,count(*) AS months,
           sum(trm_cop_usd*fx_days)/sum(fx_days) AS trm_cop_usd,
           sum(exports_usd_m) AS exports_usd_m,
           sum(imports_usd_m) AS imports_usd_m,
           sum(trade_balance_usd_m) AS trade_balance_usd_m,
           max(inflation_yoy_pct) FILTER (WHERE month=12) AS inflation_dec_pct
    FROM pp_mart.monthly GROUP BY year
), changes AS (
    SELECT *,100*(trm_cop_usd/nullif(lag(trm_cop_usd) OVER (ORDER BY year),0)-1) AS trm_annual_avg_change_pct
    FROM totals WHERE months=12
)
SELECT c.* FROM changes c CROSS JOIN pp_core.study_config s
WHERE year BETWEEN extract(year FROM s.sample_start) AND extract(year FROM s.sample_end);
