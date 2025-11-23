# app/services/features.py
import pandas as pd
from app.config import PROC_DIR

DERIVED_COLS = [
    # temporal
    "anio","mes","dia","dia_semana","franja_hora",
    # binarios cobertura
    "has_edad","has_genero","has_armas",
    # agregaciones y densidades
    "evento_id","municipio_riesgo","departamento_riesgo","modalidad",
    "tasa_delitos_muni_mes","tasa_delitos_dep_mes","acumulado_90d",
    # socio-demográficas simples (placeholders si no hay censo integrado)
    "grupo_edad_bin","es_mujer","es_hombre"
]

def build():
    df = pd.read_parquet(PROC_DIR / "master.parquet")
    df["evento_id"] = df.index
    df["modalidad"] = df.get("modalidad_hurto", df.get("delito", "SIN_DATO"))
    # Binary gender flags
    df["es_mujer"] = (df["genero"]=="FEMENINO").astype(int)
    df["es_hombre"] = (df["genero"]=="MASCULINO").astype(int)
    # Age bins
    def age_bin(s):
        s = s.fillna("SIN_DATO")
        return s.apply(lambda x: "NNA" if "NNA" in x else ("ADULTO" if "ADULTO" in x else "SIN_DATO"))
    df["grupo_edad_bin"] = age_bin(df["grupo_etario"])

    # Monthly rates per municipio/dep
    monthly = df.groupby(["departamento","municipio","anio","mes"], as_index=False)["cantidad"].sum()
    monthly["tasa_delitos_muni_mes"] = monthly["cantidad"]
    dep_monthly = df.groupby(["departamento","anio","mes"], as_index=False)["cantidad"].sum()
    dep_monthly["tasa_delitos_dep_mes"] = dep_monthly["cantidad"]
    df = df.merge(monthly[["departamento","municipio","anio","mes","tasa_delitos_muni_mes"]],
                  on=["departamento","municipio","anio","mes"], how="left")
    df = df.merge(dep_monthly[["departamento","anio","mes","tasa_delitos_dep_mes"]],
                  on=["departamento","anio","mes"], how="left")

    # Rolling 90 days per municipio
    df.sort_values(["municipio","fecha_hecho"], inplace=True)
    df["acumulado_90d"] = df.groupby("municipio")["cantidad"].rolling(window=90, min_periods=1).sum().reset_index(level=0, drop=True)

    # Risk labels (for classification baseline): top decile monthly → 1
    muni_month = df.groupby(["municipio","anio","mes"], as_index=False)["tasa_delitos_muni_mes"].mean()
    muni_month["riesgo_alto"] = muni_month["tasa_delitos_muni_mes"].transform(
        lambda s: (s >= s.quantile(0.9)).astype(int)
    )
    df = df.merge(muni_month[["municipio","anio","mes","riesgo_alto"]], on=["municipio","anio","mes"], how="left")

    # Simple risk proxies
    df["municipio_riesgo"] = df.groupby("municipio")["cantidad"].transform("sum")
    df["departamento_riesgo"] = df.groupby("departamento")["cantidad"].transform("sum")

    df.to_parquet(PROC_DIR / "features.parquet", index=False)
    print("Features built with >20 variables.")

if __name__ == "__main__":
    build()
