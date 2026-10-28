# Informe Power BI

El proyecto `PesoPulso.pbip` vincula `PesoPulso.Report` con `PesoPulso.SemanticModel`. El informe utiliza PBIR; el modelo se define en `model.bim` con formato TMSL. Ambos son editables y aptos para control de versiones, según la [documentación de Microsoft](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

## Modelo

| Tabla | Origen PostgreSQL | Granularidad |
|---|---|---|
| Calendar | `pp_mart.calendar_main` | Día calendario |
| Monthly | `pp_mart.monthly_main` | Primer día de cada mes |
| Quarterly | `pp_mart.quarterly_main` | Primer día de cada trimestre |

Calendar tiene una clave de fecha única y relaciones uno a muchos hacia ambas tablas de hechos, con filtrado desde el calendario. El filtro de año utiliza Calendar y se sincroniza entre las tres páginas. La muestra de estas vistas es 2015–2025.

El modelo contiene veinte [medidas DAX](MEDIDAS.md). Las variaciones SQL están en puntos porcentuales; las medidas las dividen por cien antes del formato porcentual. La TRM media pondera por días calendario y el Brent por cantidad de cotizaciones. Las tarjetas indican el último mes o trimestre seleccionado, para distinguirlo de un promedio del periodo o del crecimiento del año completo.

## Páginas

**Pulso macro:** tarjetas de TRM, variación interanual del dólar, inflación y crecimiento interanual del último trimestre, con evolución mensual del dólar y PIB trimestral.

**Dólar y precios:** evolución de variaciones interanuales, comparación de inflación por régimen cambiario y correlación recalculada dentro del filtro. La explicación del modelo exploratorio remite a sus resultados estadísticos.

**Sector externo:** exportaciones e importaciones FOB por año, balanza de bienes e índices de TRM y Brent con el primer mes seleccionado igual a cien.

## Conexión y compatibilidad

Los parámetros M `Server` y `Database` tienen valores predeterminados `127.0.0.1:5433` y `peso_pulso`. Las credenciales se suministran en Power BI Desktop con autenticación de base de datos; el proyecto no las almacena. El PostgreSQL local y las vistas deben existir antes de actualizar.

Power BI Desktop debe admitir proyectos PBIP y el formato mejorado PBIR; las opciones pueden depender de la versión. Se abre `PesoPulso.pbip`, se ajustan los parámetros cuando corresponda y se actualizan las consultas. El tema `theme.json` es importable para aplicar la paleta verde menta, oro y azul oscuro a series adicionales.

Para un origen CSV alternativo, las consultas de `power_query_csv.pq` reproducen las tres tablas a partir de `data/processed`. El parámetro `RepoPath` es local y no se guarda una ruta de equipo en el repositorio.

## Alcance de la validación

`reports/powerbi_validation.json` registra la validación contra esquemas oficiales, referencias a columnas y medidas, y límites del lienzo. No se ejecutó Power BI Desktop en este entorno: quedan por confirmar la apertura, las consultas M, las medidas DAX y el renderizado nativo. Las imágenes en `reports/figures` son referencias realizadas con Python y no certifican el renderizado del informe PBIR.
