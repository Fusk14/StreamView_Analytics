"""Cálculo de KPIs del catálogo StreamView (misma lógica que las cifras de control del notebook 02).
Uso:  python src/kpis.py   -> imprime los KPIs para contrastar con los scorecards de Looker Studio."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOOKER = ROOT / "data" / "processed" / "looker"


def cargar():
    return {n: pd.read_csv(LOOKER / f"{n}.csv") for n in ["catalogo_looker", "generos_long", "paises_long"]}


def calcular_kpis(cat: pd.DataFrame, paises: pd.DataFrame, generos: pd.DataFrame) -> pd.Series:
    fin = cat[cat.tiene_datos_financieros == "Sí"]          # regla 6: solo películas con datos válidos
    return pd.Series({
        "Total de contenidos": len(cat),
        "Total de películas": int((cat.type == "Movie").sum()),
        "Total de series": int((cat.type == "TV Show").sum()),
        "Países representados": paises.pais.nunique(),
        "Géneros distintos": generos.genero.nunique(),
        "Popularidad promedio": round(cat.popularity.mean(), 2),
        "Calificación promedio (solo con votos)": round(cat.vote_average_valida.mean(), 2),
        "% contenidos calificados": round(cat.calificado_num.mean() * 100, 1),
        "Películas con datos financieros": len(fin),
        "ROI agregado (ΣIngresos/ΣPresupuesto)": round(fin.revenue_valido.sum() / fin.budget_valido.sum(), 3),
        "ROI mediano por película": round(fin.roi.median(), 3),
    })


if __name__ == "__main__":
    d = cargar()
    print(calcular_kpis(d["catalogo_looker"], d["paises_long"], d["generos_long"]).to_string())
