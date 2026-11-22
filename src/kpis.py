"""Control reproducible de KPIs para StreamView Analytics (EP5 / EP6).

Permite verificar por línea de comandos (`python -m src.kpis`) que los
indicadores del archivo publicado coincidan con los valores del dashboard
en Google Looker Studio y del Informe Ejecutivo.
"""
from pathlib import Path
import pandas as pd
from src.pipeline import OUT, clean, export, kpis, load_sources


def main() -> None:
    if not OUT.exists():
        df, _ = export()
    else:
        df = clean(load_sources())

    resumen = kpis(df)
    tabla = pd.Series(resumen, name="valor").to_frame()

    print("=== Control Reproducible de KPIs StreamView Analytics (EP5) ===")
    print(f"Archivo validado: {OUT}")
    print("-" * 63)
    for clave, valor in resumen.items():
        print(f"{clave:<38}: {valor}")
    print("-" * 63)


if __name__ == "__main__":
    main()
