CREATE SCHEMA IF NOT EXISTS pp_raw;
CREATE SCHEMA IF NOT EXISTS pp_core;
CREATE SCHEMA IF NOT EXISTS pp_mart;

CREATE TABLE IF NOT EXISTS pp_raw.source_file (
    source_id text PRIMARY KEY,
    filename text NOT NULL,
    publisher text NOT NULL,
    source_url text NOT NULL,
    terms_url text NOT NULL,
    sha256 char(64) NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
    snapshot_date date NOT NULL,
    payload bytea,
    loaded_at timestamptz NOT NULL DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS pp_raw.fx_interval (
    valid_from date PRIMARY KEY,
    valid_to date NOT NULL,
    trm_cop_usd numeric(14,6) NOT NULL CHECK (trm_cop_usd > 0),
    CHECK (valid_to >= valid_from),
    source_id text NOT NULL DEFAULT 'trm' REFERENCES pp_raw.source_file(source_id)
);

CREATE TABLE IF NOT EXISTS pp_core.study_config (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    sample_start date NOT NULL,
    sample_end date NOT NULL CHECK (sample_end >= sample_start)
);

CREATE TABLE IF NOT EXISTS pp_core.calendar (
    date date PRIMARY KEY,
    year integer NOT NULL,
    month integer NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_label text NOT NULL,
    quarter_label text NOT NULL
);

CREATE TABLE IF NOT EXISTS pp_core.trm_daily (
    date date PRIMARY KEY REFERENCES pp_core.calendar(date),
    trm_cop_usd numeric(14,6) NOT NULL CHECK (trm_cop_usd > 0)
);

CREATE TABLE IF NOT EXISTS pp_core.brent_daily (
    date date PRIMARY KEY REFERENCES pp_core.calendar(date),
    brent_usd_bbl numeric(14,6) NOT NULL CHECK (brent_usd_bbl > 0)
);

CREATE TABLE IF NOT EXISTS pp_core.monthly_base (
    date date PRIMARY KEY REFERENCES pp_core.calendar(date),
    trm_cop_usd double precision NOT NULL CHECK (trm_cop_usd > 0),
    fx_days integer NOT NULL CHECK (fx_days BETWEEN 28 AND 31),
    cpi_index double precision NOT NULL CHECK (cpi_index > 0),
    exports_usd_m double precision CHECK (exports_usd_m >= 0),
    imports_usd_m double precision CHECK (imports_usd_m >= 0),
    brent_usd_bbl double precision CHECK (brent_usd_bbl > 0),
    brent_days integer CHECK (brent_days BETWEEN 1 AND 31),
    CHECK (extract(day FROM date) = 1),
    CHECK ((exports_usd_m IS NULL) = (imports_usd_m IS NULL))
);

CREATE TABLE IF NOT EXISTS pp_core.quarterly_base (
    date date PRIMARY KEY REFERENCES pp_core.calendar(date),
    gdp_real_original double precision NOT NULL CHECK (gdp_real_original > 0),
    gdp_real_sa double precision NOT NULL CHECK (gdp_real_sa > 0),
    revision text NOT NULL,
    trm_cop_usd double precision NOT NULL CHECK (trm_cop_usd > 0),
    brent_usd_bbl double precision NOT NULL CHECK (brent_usd_bbl > 0),
    exports_usd_m double precision NOT NULL CHECK (exports_usd_m >= 0),
    imports_usd_m double precision NOT NULL CHECK (imports_usd_m >= 0),
    CHECK (extract(day FROM date) = 1 AND extract(month FROM date) IN (1,4,7,10))
);

CREATE TABLE IF NOT EXISTS pp_core.pipeline_run (
    run_id uuid PRIMARY KEY,
    completed_at timestamptz NOT NULL DEFAULT current_timestamp,
    snapshot_date date NOT NULL,
    monthly_rows integer NOT NULL,
    quarterly_rows integer NOT NULL
);

COMMENT ON SCHEMA pp_raw IS 'Archivos de origen y vigencias originales de la TRM';
COMMENT ON SCHEMA pp_core IS 'Series de nivel limpias y frecuencias alineadas';
COMMENT ON SCHEMA pp_mart IS 'Indicadores analíticos y vistas para Power BI';
