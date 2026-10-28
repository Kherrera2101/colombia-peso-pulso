section PesoPulso;

shared RepoPath = "" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true];

shared Monthly =
let
    Source = Csv.Document(File.Contents(RepoPath & "/data/processed/monthly.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"date", type date}, {"trm_cop_usd", type number}, {"fx_days", Int64.Type}, {"cpi_index", type number}, {"inflation_mom_pct", type number}, {"inflation_yoy_pct", type number}, {"trm_yoy_pct", type number}, {"exports_usd_m", type number}, {"imports_usd_m", type number}, {"exports_yoy_pct", type number}, {"imports_yoy_pct", type number}, {"trade_balance_usd_m", type number}, {"brent_usd_bbl", type number}, {"brent_days", Int64.Type}, {"is_main_sample", Int64.Type}}, "en-US"),
    Sample = Table.SelectRows(Typed, each [is_main_sample] = 1)
in
    Sample;

shared Quarterly =
let
    Source = Csv.Document(File.Contents(RepoPath & "/data/processed/quarterly.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"date", type date}, {"gdp_real_original", type number}, {"gdp_real_sa", type number}, {"gdp_yoy_pct", type number}, {"gdp_qoq_sa_pct", type number}, {"trm_yoy_pct", type number}, {"is_main_sample", Int64.Type}}, "en-US"),
    Sample = Table.SelectRows(Typed, each [is_main_sample] = 1)
in
    Sample;

shared Calendar =
let
    Source = Csv.Document(File.Contents(RepoPath & "/data/processed/calendar.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"date", type date}, {"year", Int64.Type}, {"month", Int64.Type}}, "en-US"),
    Sample = Table.SelectRows(Typed, each [year] >= 2015 and [year] <= 2025)
in
    Sample;
