# StreamView Analytics — Solución Integral de Visual Analytics (EP5 / EP6)

Proyecto de Visualización de Datos (`ADY1104`) desarrollado sobre los dos conjuntos de datos corporativos del caso semestral **StreamView Analytics** (`netflix_movies_detailed_up_to_2025.csv` y `netflix_tv_shows_detailed_up_to_2025.csv`).

> **Nota metodológica:** Los datos provienen de un catálogo muestreado y enriquecido con metadatos públicos (TMDb); no representan registros operacionales de reproducciones ni retención de suscriptores.

## Mejoras y Decisiones Metodológicas (EP5)
- **Deduplicación e integridad de claves:** Se consolidan 9 repeticiones de `(type, show_id)` detectadas en series, pasando de 32.000 registros brutos a **31.991 títulos únicos** identificados mediante la clave compuesta `content_key` (`M_` / `S_` + `show_id`).
- **Tratamiento de valores faltantes:** Se conservan los nulos estructurales (`NaN`) sin transformarlos en categorías artificiales dentro de los rankings visuales, aplicando filtros locales por visualización.
- **Asignación de género y país principal:** Para evitar el doble conteo en una tabla única de grano título, los gráficos y segmentadores emplean `genero_principal` y `pais_principal`, manteniendo la cadena multi-género completa en `generos_armonizados`.
- **Umbral de valoración confiable ($\ge 50$ votos):** Las comparaciones de calidad utilizan `nota_confiable_50` (`15.397` títulos elegibles; media global `6,63`, con `7,52` en series frente a `6,39` en películas).
- **Popularidad normalizada por formato:** Se incorpora `popularidad_percentil_tipo` (0–100) para evaluar la posición relativa dentro de `Movie` y `TV Show` sin mezclar distribuciones incompatibles.
- **Rigor en métricas financieras (exclusivo películas):** Sobre las **3.492 películas** con presupuesto e ingresos $\ge \text{US\$ } 10.000$ (`finanzas_validas = True`), se distingue entre **tasa de recuperación presupuestaria** (`63,86 %`), **múltiplo agregado de recaudación** (`2,924x`) y **ROI neto estimado** (`192,41 %`).

## Estructura del Repositorio
```text
data/
├── raw/                                  # Fuentes originales inmutables (Movies y TV Shows)
└── processed/looker/                     # Exportación única: catalogo_looker_ep5.csv (31.991 filas)
notebooks/
├── 00_UnionDataset.ipynb                 # Integración y auditoría inicial de fuentes
├── 01_Limpieza_dataset.ipynb             # Deduplicación, reglas de calidad y tratamiento
├── 02_preparacion_looker_studio.ipynb    # Generación y validación del CSV para Looker Studio
└── 03_eda_visualizaciones.ipynb          # Análisis exploratorio y exportación de figuras estáticas
src/
├── pipeline.py                           # Pipeline ETL centralizado y reproducible
└── kpis.py                               # Script de verificación de cifras de control
images/                                   # Gráficos estáticos del EDA exportados en alta resolución
dashboard/
└── GUIA_LOOKER.md                        # Especificación técnica de construcción en Looker Studio
requirements.txt                          # Dependencias del entorno Python
```

## Ejecución y Reproducibilidad
Requiere Python 3.10+. Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python -c "from src.pipeline import export; export()"
python -m src.kpis
```

Para explorar o reejecutar los cuadernos interactivos en orden (`00` $\rightarrow$ `01` $\rightarrow$ `02` $\rightarrow$ `03`):
```bash
jupyter lab
```
- El cuaderno `02_preparacion_looker_studio.ipynb` genera `data/processed/looker/catalogo_looker_ep5.csv`.
- El cuaderno `03_eda_visualizaciones.ipynb` exporta las 6 figuras estáticas en `images/`.

## Cifras de Control Verificadas (`python -m src.kpis`)
| Indicador | Valor Verificado | Alcance / Filtro |
| :--- | :--- | :--- |
| **Títulos únicos (`content_key`)** | `31.991` | Catálogo consolidado (`16.000` películas y `15.991` series) |
| **Títulos con $\ge 50$ votos** | `15.397` | `tiene_50_votos = 1` (`48,13 %` del catálogo) |
| **Nota media confiable** | `6,626` (`6,63`) | `TV Show`: `7,52` (`n = 3.212`) vs. `Movie`: `6,39` (`n = 12.185`) |
| **Películas con finanzas válidas** | `3.492` | `type = Movie` con `budget >= 10.000` y `revenue >= 10.000` |
| **Porcentaje de recuperación** | `63,86 %` | Proporción de películas válidas con `ingresos >= presupuesto` |
| **Múltiplo agregado de ingresos** | `2,9241x` (`2,92x`) | `SUM(ingresos_usd) / SUM(presupuesto_usd)` |
| **ROI neto estimado** | `192,41 %` | `(SUM(ingresos_usd) - SUM(presupuesto_usd)) / SUM(presupuesto_usd)` |

## Arquitectura del Dashboard en Google Looker Studio
El tablero interactivo se alimenta exclusivamente de `data/processed/looker/catalogo_looker_ep5.csv` y se organiza en tres vistas jerárquicas con controles globales (`Año estreno`, `Tipo de título`, `Género`, `País`, `Idioma`):
1. **Vista 1 — Resumen Ejecutivo (`¿Cómo está compuesto el catálogo?`):** KPIs de volumen, composición por género principal, Top 5 de títulos con $\ge 50$ votos y mercados líderes por volumen de producción.
2. **Vista 2 — Exploración y Calidad (`¿Qué géneros destacan y cómo se valoran?`):** Treemap de presencia por género, dispersión de percentil de popularidad vs. nota confiable y evolución temporal de calificación por formato (2010–2025).
3. **Vista 3 — Mercados y Finanzas (`¿Qué mercados y títulos conviene priorizar?`):** Cobertura geográfica mundial (mapa coroplético), ranking de idiomas y desempeño financiero por tramo presupuestario en películas.
