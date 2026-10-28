# Validación del corte

Ejecución local del 28 de octubre de 2026, con Python 3.12 y PostgreSQL 17.11.

| Componente | Resultado |
|---|---|
| Reconstrucción desde originales locales | Completada: 153 meses y 50 trimestres conservados; muestra principal de 132 y 44. |
| Pruebas automatizadas | 10 superadas. |
| Carga PostgreSQL | Confirmada dentro de una transacción; seis archivos originales archivados y 3.025 vigencias TRM. |
| Indicadores mensuales | Siete conciliados entre SQL y Python; error absoluto máximo inferior a `3e-10`. |
| Indicadores trimestrales | Cuatro conciliados; error absoluto máximo inferior a `6e-11`. |
| Agregados anuales | Seis indicadores conciliados en once años completos. |
| Consultas analíticas SQL | Archivo completo ejecutado con parada ante errores. |
| Notebook | Siete celdas de código ejecutadas, con tablas y gráfico conservados. |
| Láminas | Tres imágenes revisadas visualmente. |
| Power BI | 36 archivos contrastados con esquemas oficiales; 32 referencias a campos y medidas comprobadas. |
| Power BI Desktop | Apertura, actualización, ejecución DAX y renderizado nativo pendientes de validación. |

La validación de esquemas Power BI verifica estructura, referencias y límites del lienzo; no garantiza por sí sola la compatibilidad de ejecución del motor tabular ni de los visuales. Las cifras son del snapshot documentado y pueden diferir de revisiones posteriores.

Evidencias detalladas: `data_quality.json`, `database_validation.json` y `powerbi_validation.json`. Las pruebas de transformación y consistencia están en `tests/`.
