# StreamView Analytics — EP5 (versión corregida)

Proyecto académico de Visualización de Datos, sobre los dos CSV originales del caso semestral. **No son datos reales de uso o retención de una plataforma**.

## Qué cambió respecto a EP2
- Se consolidan 9 repeticiones de `(type, show_id)` observadas en TV Show: 32.000 registros de origen → **31.991 títulos únicos**. Ante conflicto se prioriza el mayor número de votos y después popularidad. Este criterio no presupone temporalidad.
- Se mantienen faltantes como `NaN` sin convertirlos en categorías falsas como `Sin dato`.
- Se utilizan géneros principales únicos para el filtro de Looker, y se conserva una cadena informativa de todos los géneros armonizados. No se cuenta simultáneamente una obra en varias categorías con esta exportación plana.
- La nota principal exige al menos 50 votos; popularidad se muestra por formato o como percentil dentro de tipo.
- `revenue / budget` se denomina **múltiplo de ingresos/presupuesto**, no ROI neto. El campo `roi_neto` se entrega como métrica separada y aproximada.
- Se corrige el porcentaje de películas que recuperan presupuesto y se documenta la submuestra válida.
- Se generan **un único CSV de publicación** y seis gráficos estáticos.

## Estructura
```
data/raw/                 # Fuentes originales inmutables
 data/processed/looker/          # Solo catalogo_looker_ep5.csv
notebooks/                # 00, 01, 02, 03 (en ese orden)
src/pipeline.py           # Lógica de datos centralizada
src/kpis.py               # Control reproducible
images/                   # Gráficos exportados por notebook 03
dashboard/                # Guía de reconstrucción Looker
reports/                  # Informe EP5, infografía y resumen futuro
```

## Ejecución
Requiere Python 3.10+; desde la raíz del proyecto:
```bash
python -m pip install -r requirements.txt
jupyter lab
```
Abrir notebooks en orden 00 → 01 → 02 → 03, o generar el CSV directamente:
```bash
python -c "from src.pipeline import export; export()"
python -m src.kpis
```
Notebook 02 genera `data/processed/catalogo_looker_ep5.csv`; notebook 03 genera PNG en `images/`.

## Advertencias de negocio y datos
- No calcular tasas de fidelidad o engagement sin datos de usuario.
- No inferir evolución del negocio de un muestreo de exactamente 1.000 registros de cada tipo por año.
- No comparar medias brutas de popularidad entre Movie y TV Show como equivalentes; `popularidad_percentil_tipo` es una normalización de posición dentro de cada tipo, no medición de visualizaciones.
- Las películas sin datos financieros >=US$10.000 se excluyen del análisis económico, no de las demás vistas.
- Los análisis de género en el **CSV único** corresponden a `genero_principal`, no a aparición en cualquier género. El modelo multi-etiqueta completo requeriría otra tabla con distinto grano.
- El umbral de 50 votos es un criterio de calidad del análisis, no prueba de representatividad estadística.

## Dashboard
Conecta Looker Studio al CSV publicado e implementa las instrucciones precisas del notebook 02 y `dashboard/GUIA_LOOKER.md`.
**Enlace dashboard EP5:** pendiente de crear/publicar desde la cuenta del equipo.

## Evidencias pendientes para cierre EP5
El informe PDF, resumen ejecutivo e infografía deben actualizarse con los resultados de este pipeline después de validar el nuevo dashboard.
