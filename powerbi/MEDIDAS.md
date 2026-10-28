# Medidas del modelo

Las tasas almacenadas en puntos porcentuales se dividen por 100 antes de aplicar el formato de porcentaje de Power BI. Los importes comerciales se expresan en millones de USD FOB.

## TRM promedio

TRM ponderada por días calendario dentro de la selección.

```dax
TRM promedio = DIVIDE(SUMX(Monthly, Monthly[trm_cop_usd] * Monthly[fx_days]), SUM(Monthly[fx_days]))
```

## TRM último mes

Promedio de TRM del último mes de la selección.

```dax
TRM último mes = VAR D = MAX(Monthly[date]) RETURN CALCULATE(MAX(Monthly[trm_cop_usd]), KEEPFILTERS(Monthly[date] = D))
```

## Cambio TRM interanual

Media de variaciones interanuales; no es la variación de la TRM media anual.

```dax
Cambio TRM interanual = DIVIDE(AVERAGE(Monthly[trm_yoy_pct]), 100)
```

## Cambio TRM último mes

Variación interanual del promedio mensual de TRM en el último mes.

```dax
Cambio TRM último mes = VAR D = MAX(Monthly[date]) RETURN CALCULATE(DIVIDE(MAX(Monthly[trm_yoy_pct]), 100), KEEPFILTERS(Monthly[date] = D))
```

## Inflación interanual

Media de inflación interanual de los meses seleccionados.

```dax
Inflación interanual = DIVIDE(AVERAGE(Monthly[inflation_yoy_pct]), 100)
```

## Inflación último mes

Inflación interanual del último mes seleccionado.

```dax
Inflación último mes = VAR D = MAX(Monthly[date]) RETURN CALCULATE(DIVIDE(MAX(Monthly[inflation_yoy_pct]), 100), KEEPFILTERS(Monthly[date] = D))
```

## Inflación mensual

Variación mensual del índice IPC.

```dax
Inflación mensual = DIVIDE(AVERAGE(Monthly[inflation_mom_pct]), 100)
```

## Exportaciones FOB

Exportaciones de bienes en millones de USD FOB.

```dax
Exportaciones FOB = SUM(Monthly[exports_usd_m])
```

## Importaciones FOB

Importaciones de bienes en millones de USD FOB.

```dax
Importaciones FOB = SUM(Monthly[imports_usd_m])
```

## Balanza de bienes

Exportaciones menos importaciones, ambas FOB; millones de USD.

```dax
Balanza de bienes = [Exportaciones FOB] - [Importaciones FOB]
```

## Brent promedio

Precio Brent ponderado por observaciones hábiles, USD por barril.

```dax
Brent promedio = DIVIDE(SUMX(Monthly, Monthly[brent_usd_bbl] * Monthly[brent_days]), SUM(Monthly[brent_days]))
```

## Cambio exportaciones interanual

Media de variaciones interanuales nominales de exportaciones.

```dax
Cambio exportaciones interanual = DIVIDE(AVERAGE(Monthly[exports_yoy_pct]), 100)
```

## Cambio importaciones interanual

Media de variaciones interanuales nominales de importaciones.

```dax
Cambio importaciones interanual = DIVIDE(AVERAGE(Monthly[imports_yoy_pct]), 100)
```

## Meses observados

Cantidad de meses en el contexto de filtro.

```dax
Meses observados = COUNTROWS(Monthly)
```

## PIB crecimiento interanual

Crecimiento real interanual; en más de un trimestre muestra la media.

```dax
PIB crecimiento interanual = DIVIDE(AVERAGE(Quarterly[gdp_yoy_pct]), 100)
```

## PIB último trimestre

Crecimiento real interanual del último trimestre seleccionado, no del año completo.

```dax
PIB último trimestre = VAR D = MAX(Quarterly[date]) RETURN CALCULATE(DIVIDE(MAX(Quarterly[gdp_yoy_pct]), 100), KEEPFILTERS(Quarterly[date] = D))
```

## PIB variación trimestral SA

Variación trimestral del PIB ajustado por estacionalidad y calendario.

```dax
PIB variación trimestral SA = DIVIDE(AVERAGE(Quarterly[gdp_qoq_sa_pct]), 100)
```

## Índice TRM

Primer mes de la selección = 100.

```dax
Índice TRM = VAR D = MINX(ALLSELECTED(Calendar), Calendar[date]) VAR B = CALCULATE([TRM promedio], REMOVEFILTERS(Calendar), Calendar[date] = D) RETURN 100 * DIVIDE([TRM promedio], B)
```

## Índice Brent

Primer mes de la selección = 100.

```dax
Índice Brent = VAR D = MINX(ALLSELECTED(Calendar), Calendar[date]) VAR B = CALCULATE([Brent promedio], REMOVEFILTERS(Calendar), Calendar[date] = D) RETURN 100 * DIVIDE([Brent promedio], B)
```

## Correlación TRM inflación

Pearson r contemporáneo sobre pares de meses, recalculado al filtrar.

```dax
Correlación TRM inflación = VAR S = FILTER(ADDCOLUMNS(VALUES(Calendar[month_label]), "X", CALCULATE(AVERAGE(Monthly[trm_yoy_pct])), "Y", CALCULATE(AVERAGE(Monthly[inflation_yoy_pct]))), NOT ISBLANK([X]) && NOT ISBLANK([Y])) VAR N = COUNTROWS(S) VAR SX = SUMX(S, [X]) VAR SY = SUMX(S, [Y]) VAR SXX = SUMX(S, [X] * [X]) VAR SYY = SUMX(S, [Y] * [Y]) VAR SXY = SUMX(S, [X] * [Y]) RETURN IF(N > 2, DIVIDE(N * SXY - SX * SY, SQRT(MAX(0, (N * SXX - SX * SX) * (N * SYY - SY * SY)))))
```
