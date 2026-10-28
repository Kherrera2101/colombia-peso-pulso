# Diccionario de datos

Los CSV utilizan UTF-8, punto decimal y fechas ISO. Las tasas se almacenan como porcentajes: `5.1` significa 5,1%, no 510%. Las celdas vacías son datos no disponibles.

| Variable | Unidad | Definición |
|---|---|---|
| `date` | Fecha | Inicio del mes o trimestre; en series diarias, día observado. |
| `trm_cop_usd` | COP/USD | Media calendario de la TRM en tablas agregadas; valor vigente en tabla diaria. |
| `fx_days` | Días | Días calendario usados como ponderación de TRM. |
| `cpi_index` | Índice | IPC nacional empalmado; diciembre de 2018 = 100. |
| `exports_usd_m` | Millones de USD FOB | Exportaciones nominales de bienes. |
| `imports_usd_m` | Millones de USD FOB | Importaciones nominales de bienes, en valoración FOB. |
| `trade_balance_source_usd_m` | Millones de USD FOB | Balanza publicada en el anexo; referencia de conciliación. |
| `trade_balance_usd_m` | Millones de USD FOB | Exportaciones menos importaciones. |
| `brent_usd_bbl` | USD/barril | Precio Europe Brent Spot FOB; media de cotizaciones en tablas agregadas. |
| `brent_days` | Observaciones | Cantidad de cotizaciones publicadas en el mes. |
| `gdp_real_original` | Miles de millones de COP de referencia 2015 | PIB trimestral real, serie original encadenada de volumen. |
| `gdp_real_sa` | Miles de millones de COP de referencia 2015 | PIB real ajustado por estacionalidad y calendario. |
| `gdp_yoy_pct` | % | 100 × (PIB original / PIB original de cuatro trimestres antes − 1). |
| `gdp_qoq_sa_pct` | % | 100 × (PIB ajustado / PIB ajustado del trimestre anterior − 1). |
| `trm_qoq_pct` | % | Cambio respecto al trimestre anterior de la TRM media calendario. |
| `revision` | Categoría | Marca preliminar, provisional o sin marca tomada del encabezado del PIB. |
| `year` | Año | Año calendario. |
| `month` | Mes | Entero entre 1 y 12. |
| `quarter` | Trimestre | Entero entre 1 y 4. |
| `regime` | Categoría | Apreciación si la TRM media cae frente al mismo mes del año anterior; depreciación si sube. |
| `is_main_sample` | 0/1 | Uno para las fechas de 2015–2025 de la muestra principal. |
| `is_complete` | 0/1 | Uno cuando hay nivel válido de TRM, IPC, comercio y Brent. |
| `month_label` | Texto AAAA-MM | Etiqueta ordenable para categorías mensuales. |
| `quarter_label` | Texto AAAA-Tn | Etiqueta ordenable para categorías trimestrales. |
| `trm_mom_pct` | % | Variación porcentual de TRM media frente al mes previo; no es una fracción entre cero y uno. |
| `trm_yoy_pct` | % | Variación porcentual de TRM media frente al mismo mes del año anterior; no es una fracción entre cero y uno. |
| `inflation_mom_pct` | % | Variación porcentual de IPC frente al mes previo; no es una fracción entre cero y uno. |
| `inflation_yoy_pct` | % | Variación porcentual de IPC frente al mismo mes del año anterior; no es una fracción entre cero y uno. |
| `exports_mom_pct` | % | Variación porcentual de exportaciones nominales FOB frente al mes previo; no es una fracción entre cero y uno. |
| `exports_yoy_pct` | % | Variación porcentual de exportaciones nominales FOB frente al mismo mes del año anterior; no es una fracción entre cero y uno. |
| `imports_mom_pct` | % | Variación porcentual de importaciones nominales FOB frente al mes previo; no es una fracción entre cero y uno. |
| `imports_yoy_pct` | % | Variación porcentual de importaciones nominales FOB frente al mismo mes del año anterior; no es una fracción entre cero y uno. |
| `brent_mom_pct` | % | Variación porcentual de Brent medio frente al mes previo; no es una fracción entre cero y uno. |
| `brent_yoy_pct` | % | Variación porcentual de Brent medio frente al mismo mes del año anterior; no es una fracción entre cero y uno. |

## Archivos

| Archivo | Granularidad | Filas |
|---|---|---|
| `monthly.csv` | Mes, 2014–sep 2026 | 153 |
| `quarterly.csv` | Trimestre, 2014–T2 2026 | 50 |
| `trm_daily.csv` | Día calendario, 2014–sep 2026 | 4,656 |
| `brent_daily.csv` | Día con cotización, 2014–sep 2026 | 3,235 |
| `calendar.csv` | Día calendario | 4,656 |

El detalle de la fuente y su versión está en `source_manifest.json`. Las tablas `reports/correlations.csv` y `reports/gdp_correlations.csv` incluyen `n` y la definición de muestra para cada par; `model_coefficients.csv` conserva coeficientes, errores HAC e intervalos.
