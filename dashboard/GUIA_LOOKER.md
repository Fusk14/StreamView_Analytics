# Guía de reconstrucción del dashboard

1. Haz una copia del dashboard EP2 antes de modificarlo. Reemplaza la fuente de datos por `data/processed/looker/catalogo_looker_ep5.csv`.
2. Confirma configuración regional y tipos decimales. Verifica `MAX(popularity)` cercano a 6.422, **no millones**.
3. Usa `COUNT_DISTINCT(content_key)` para títulos y `AVG(nota_confiable_50)` para nota. Excluye nulos en gráficos de notas.
4. Filtros compartidos: año de estreno, formato, `genero_principal`, `pais_principal`, `idioma_nombre`. Finanzas: filtro fijo `finanzas_validas = TRUE`.
5. Finanzas: múltiplo agregado = `SUM(ingresos_usd)/SUM(presupuesto_usd)`; recuperación = porcentaje de `recupera_presupuesto = true` entre finanzas válidas. Valores base aproximados: 2,924× y 63,86%.
6. Evita usar la tabla única para conteos multi-etiqueta; la clasificación por género es únicamente principal.
7. Consistencia: Movie azul #3366CC; TV Show naranja #E68A2E. Elimina la torta 50/50, barras constantes por año y comparaciones crudas de popularidad entre formatos.
8. Títulos que comuniquen hallazgos, `n` visible, etiquetas en español, ejes sin nombres técnicos, sin `Sin dato` en rankings (los faltantes se informan aparte).
9. Reconciliar cada indicador con `python -m src.kpis` y la tabla del notebook 03, tanto en vista general como al aplicar filtros.
10. Documenta capturas antes/después y agrega URL accesible de Looker al README una vez publicado.
