# Metodología

## Pregunta y alcance

El análisis examina asociaciones entre la tasa de cambio nominal y medidas de actividad, precios y comercio de Colombia. La unidad de observación es el mes en precios y comercio; en PIB es el trimestre. La muestra principal, enero de 2015–diciembre de 2025, contiene 132 meses y 44 trimestres. Los datos de 2014 permiten calcular variaciones interanuales al inicio de la muestra.

No hay un instrumento, experimento natural ni estrategia de identificación causal. Los signos de las correlaciones no determinan si la apreciación mejora o empeora el bienestar, la competitividad o el crecimiento.

## Frecuencias y unidades

La TRM está expresada en **COP por USD**. Un descenso representa apreciación del peso. Cada registro incluye un comienzo y un final de vigencia inclusivos. El flujo expande esos intervalos y promedia todos los días calendario del mes; evita dar el mismo peso a una vigencia de un día y a otra que cubre un fin de semana. La TRM trimestral pondera las medias mensuales por sus días calendario.

El IPC es un índice empalmado con base diciembre de 2018 = 100. La inflación mensual es `100 × (IPC_t / IPC_t−1 − 1)`; la interanual es `100 × (IPC_t / IPC_t−12 − 1)`. Los índices del anexo están redondeados a dos decimales, por lo que las tasas recalculadas pueden diferir ligeramente de tasas publicadas con mayor precisión interna.

Las exportaciones y las importaciones son flujos mensuales de bienes en **millones de USD FOB**. La balanza es su diferencia. No se resta una importación CIF de una exportación FOB. Tampoco se interpreta el valor comercial nominal como volumen físico o como crecimiento real. El total trimestral exige tres meses disponibles; el anual, doce.

El Brent se expresa en USD por barril. La media mensual utiliza las cotizaciones publicadas; no se imputan fines de semana ni ausencias. La media trimestral pondera por el número de cotizaciones, no por días calendario.

El PIB real corresponde a series encadenadas de volumen con referencia 2015, en miles de millones de pesos. El crecimiento interanual compara la serie original con el mismo trimestre del año anterior; el crecimiento trimestral compara niveles de la serie ajustada por estacionalidad y calendario. No se interpola PIB mensual. El crecimiento anual usa la suma de cuatro niveles originales frente a la suma del año anterior. Se conservan las marcas preliminar y provisional del anexo; las cifras pueden revisarse.

## Asociaciones y rezagos

Se calculan Pearson y Spearman sobre variaciones, con pares completos. En los análisis mensuales, `k` relaciona TRM interanual de `t−k` con el indicador de `t`. Los rezagos son 0, 1, 3, 6 y 12 meses; se muestran todos, sin seleccionar únicamente el mayor. La muestra efectiva disminuye con el rezago porque el historial descargado de TRM empieza en 2014 y sus variaciones interanuales empiezan en 2015. Cada fila conserva su `n`.

Las correlaciones que excluyen 2020–2021 evalúan sensibilidad al choque y al rebote de la pandemia. Son una comparación descriptiva, no una corrección causal. Las observaciones interanuales comparten meses de referencia y presentan dependencia temporal; no se usan valores p de Pearson ordinarios para declarar descubrimientos confirmatorios.

## Modelo exploratorio

La variable dependiente es la inflación mensual. Los regresores son tres rezagos de la variación porcentual mensual de TRM, un rezago de Brent mensual, un rezago de inflación mensual, once indicadores de mes y un indicador de marzo de 2020 a diciembre de 2021. El ajuste OLS utiliza covarianza HAC con ventana de doce filas mensuales y ponderación Bartlett.

La suma de los tres coeficientes cambiarios y su intervalo se obtiene usando toda la matriz de covarianza, incluidas covarianzas entre coeficientes. El intervalo usa la aproximación normal de 1,96 errores estándar. La suma describe la asociación de una variación cambiaria de un mes con los tres meses posteriores manteniendo los controles; no constituye un multiplicador causal ni un efecto de largo plazo, y no incorpora la propagación dinámica completa de la inflación rezagada.

Se reportan ADF en logaritmos de niveles y variaciones mensuales, y Ljung–Box en residuos. En este corte, ADF no rechaza raíz unitaria en inflación mensual al 5% (`p≈0,36`). HAC no resuelve esa incertidumbre, ni los cambios de régimen, endogeneidad o variables omitidas. El modelo se presenta como exploratorio. No se entregan pronósticos ni métricas de desempeño fuera de muestra.

## Calidad y trazabilidad

Los archivos de origen tienen URL y SHA-256. Una descarga con huella distinta se detiene. La carga PostgreSQL es atómica, usa un bloqueo por proyecto y archiva el contenido original cuando está disponible. Si se carga únicamente el snapshot procesado, conserva la procedencia, pero `payload` queda nulo y no se reconstruyen vigencias originales ausentes.

Las validaciones comprueban cobertura mensual y trimestral, fechas únicas, valores finitos, unidades, identidad de balanza y expansión de vigencias. No se imputan observaciones faltantes. La falta de comercio de septiembre de 2026 permanece como nulo; el último mes común de las series mensuales es agosto de 2026 y el último trimestre del PIB es abril–junio de 2026.

SQL vuelve a calcular las tasas con `LAG`; no toma de Python las columnas derivadas conciliadas. El informe de validación cuantifica el error numérico entre ambas implementaciones. Los resultados de 2026 se conservan como actualización parcial y no se mezclan con los promedios de años completos.
