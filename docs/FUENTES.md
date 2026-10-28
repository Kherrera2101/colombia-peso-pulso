# Fuentes y corte documental

Consulta de referencia: **28 de octubre de 2026**. Las URL de descarga, los tamaños y las huellas SHA-256 están fijados en `config/sources.json`. Los archivos originales se guardan en `data/raw` y quedan fuera del control de versiones.

| Serie | Productor | Frecuencia y unidad | Última observación usada |
|---|---|---|---|
| [IPC: índice empalmado, diciembre de 2018 = 100](https://www.dane.gov.co/index.php/estadisticas-por-tema/precios-y-costos/indice-de-precios-al-consumidor-ipc) | DANE | mensual · índice | 2026-09-01 |
| [PIB real, series originales y ajustadas, referencia 2015](https://www.dane.gov.co/index.php/estadisticas-por-tema/cuentas-nacionales/cuentas-nacionales-trimestrales/pib-informacion-tecnica) | DANE | trimestral · miles de millones de COP de 2015 | 2026-04-01 |
| [Exportaciones e importaciones de bienes, ambas FOB](https://www.dane.gov.co/index.php/estadisticas-por-tema/comercio-internacional/balanza-comercial) | DIAN–DANE | mensual · millones de USD FOB | 2026-08-01 |
| [Europe Brent Spot Price FOB](https://www.eia.gov/dnav/pet/hist/RBRTED.htm) | U.S. Energy Information Administration | diaria hábil · USD por barril | 2026-09-30 (límite del corte; solo cotizaciones publicadas) |
| [Tasa de cambio representativa del mercado](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-Historic/mcec-87by) | Superintendencia Financiera de Colombia | intervalo de vigencia · COP por USD | 2026-09-30 |

## Descargas

### ipc.xlsx

[Archivo o API original](https://www.dane.gov.co/files/operaciones/IPC/sep2026/anex-IPC-Indices-sep2026.xlsx) · [Condiciones de uso](https://www.dane.gov.co/index.php/terrminos-y-condiciones-dane)

SHA-256: `56f8e5e6e9d235d411e487b2284beba1be8eaeee69b7b9516bfa8ea8443c0676`

### pib.xlsx

[Archivo o API original](https://www.dane.gov.co/files/operaciones/PIB/anex-ProduccionConstantes-IItrim2026.xlsx) · [Condiciones de uso](https://www.dane.gov.co/index.php/terrminos-y-condiciones-dane)

SHA-256: `1ece527765811c8b412d308201e5b2a2ab814f08f6e1e9c22888fceefb91ff04`

### trade.xlsx

[Archivo o API original](https://www.dane.gov.co/files/operaciones/BCOM/anex-BCOM-Mensual-ago2026.xlsx) · [Condiciones de uso](https://www.dane.gov.co/index.php/terrminos-y-condiciones-dane)

SHA-256: `e7b0df09924b23f3e9e3bb4901cf50996060b2ba354ae715f9bfdcb2e5ecd96f`

### brent.xls

[Archivo o API original](https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls) · [Condiciones de uso](https://www.eia.gov/about/copyrights_reuse.php)

SHA-256: `c7c1e1eeb321fa5982f74747886963b35bd2df3c2f63960271c353421d5830ca`

### trm.json

[Archivo o API original](https://www.datos.gov.co/resource/mcec-87by.json?%24where=vigenciadesde+%3E%3D+%272013-12-20T00%3A00%3A00%27+AND+vigenciadesde+%3C+%272026-10-01T00%3A00%3A00%27&%24order=vigenciadesde&%24limit=20000) · [Condiciones de uso](https://creativecommons.org/licenses/by-sa/4.0/)

SHA-256: `d35f7e1a8884741ee20b0073c6a71091c211fb3c5ce8747a6e692494f36a95ce`

### trm_metadata.json

[Archivo o API original](https://www.datos.gov.co/api/views/mcec-87by.json) · [Condiciones de uso](https://herramientas.datos.gov.co/terminos)

SHA-256: `1af036002f3c6dfef97d60e4ec7bf636705b9d36eadfbee663a02ce700709f11`

## TRM y trazabilidad

Fuente: Portal de Datos Abiertos www.datos.gov.co. Productor: Superintendencia Financiera de Colombia. Metadatos del conjunto `mcec-87by`: licencia `CC_40_BY_SA`; última actualización del conjunto en UTC: `2026-10-28T21:16:35+00:00`. La consulta de observaciones limita el comienzo de vigencia a fechas anteriores al 1 de octubre de 2026; esa limitación es distinta de la fecha de actualización de los metadatos.

El anexo IPC fue actualizado el 7 de octubre de 2026, el de PIB el 18 de agosto de 2026 y el de balanza de bienes el 21 de octubre de 2026. Los anexos contienen cifras revisables. Las huellas identifican el archivo exacto, no una versión inmutable de toda la API.

Los enlaces de EIA y los metadatos del portal son mutables. La reproducción estadística usa el snapshot procesado versionado. Una reconstrucción desde descargas nuevas exige revisar cualquier diferencia de huella y documentar otro corte.
