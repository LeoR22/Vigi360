# app/services/features.py
import pandas as pd
from app.config import PROC_DIR

DERIVED_COLS = [
    "anio","mes","dia","dia_semana","franja_hora",
    "has_edad","has_genero","has_armas",
    "evento_id","municipio_riesgo","departamento_riesgo","modalidad",
    "tasa_delitos_muni_mes_lag","tasa_delitos_dep_mes_lag","acumulado_90d",
    "grupo_edad_bin","es_mujer","es_hombre","riesgo_alto"
]

def build():
    df = pd.read_parquet(PROC_DIR / "master.parquet")

    # Filtro por departamento Santander
    if "departamento" in df.columns:
        df = df[df["departamento"] == "SANTANDER"].copy()

    # Identificador de evento
    df["evento_id"] = df.index

    # Modalidad del delito
    df["modalidad"] = df.get("modalidad_hurto", df.get("delito", "SIN_DATO"))

    # Binary gender flags
    df["es_mujer"] = (df.get("genero", "") == "FEMENINO").astype(int)
    df["es_hombre"] = (df.get("genero", "") == "MASCULINO").astype(int)

    # Age bins
    def age_bin(s):
        s = s.fillna("SIN_DATO")
        return s.apply(lambda x: "NNA" if "NNA" in x else ("ADULTO" if "ADULTO" in x else "SIN_DATO"))
    if "grupo_etario" in df.columns:
        df["grupo_edad_bin"] = age_bin(df["grupo_etario"])
    else:
        df["grupo_edad_bin"] = "SIN_DATO"

    # Asegurar tipos
    df["fecha_hecho"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0)

    # Monthly rates por municipio
    if "municipio" in df.columns:
        monthly = df.groupby(["departamento","municipio","anio","mes"], as_index=False)["cantidad"].sum()
        monthly["tasa_delitos_muni_mes"] = monthly["cantidad"]

        # Lag municipal
        monthly["tasa_delitos_muni_mes_lag"] = monthly.sort_values(["municipio","anio","mes"]) \
            .groupby("municipio")["tasa_delitos_muni_mes"].shift(1)

        df = df.merge(
            monthly[["departamento","municipio","anio","mes","tasa_delitos_muni_mes_lag"]],
            on=["departamento","municipio","anio","mes"], how="left"
        )
    else:
        df["tasa_delitos_muni_mes_lag"] = 0

    # Monthly rates por departamento y lag
    dep_monthly = df.groupby(["departamento","anio","mes"], as_index=False)["cantidad"].sum()
    dep_monthly["tasa_delitos_dep_mes"] = dep_monthly["cantidad"]
    dep_monthly["tasa_delitos_dep_mes_lag"] = dep_monthly.sort_values(["departamento","anio","mes"]) \
        .groupby("departamento")["tasa_delitos_dep_mes"].shift(1)

    df = df.merge(
        dep_monthly[["departamento","anio","mes","tasa_delitos_dep_mes_lag"]],
        on=["departamento","anio","mes"], how="left"
    )

    # Rolling 90 días por municipio
    if "municipio" in df.columns:
        df = df.sort_values(["municipio","fecha_hecho"])
        def rolling_90d(group):
            g = group.set_index("fecha_hecho").sort_index()
            out = group.copy()
            out["acumulado_90d"] = g["cantidad"].rolling("90D").sum().values
            return out
        df = df.groupby("municipio", group_keys=False).apply(rolling_90d)
    else:
        df["acumulado_90d"] = 0

    # Riesgo alto por mes (top 10% de municipios en cada anio-mes)
    if "municipio" in df.columns:
        muni_month = monthly.copy()
        # Para cada (anio, mes), marcamos como 1 a los municipios con tasa en el top 10% de ese mes
        muni_month["riesgo_alto"] = muni_month.groupby(["anio","mes"])["tasa_delitos_muni_mes"] \
            .transform(lambda s: (s >= s.quantile(0.9)).astype(int))

        df = df.merge(
            muni_month[["departamento","municipio","anio","mes","riesgo_alto"]],
            on=["departamento","municipio","anio","mes"], how="left"
        )
    else:
        df["riesgo_alto"] = 0

    # Proxies de riesgo
    if "municipio" in df.columns:
        df["municipio_riesgo"] = df.groupby("municipio")["cantidad"].transform("sum")
    else:
        df["municipio_riesgo"] = 0
    df["departamento_riesgo"] = df.groupby("departamento")["cantidad"].transform("sum")

    # Imputación segura post-merge para evitar NaNs en features
    for col in ["tasa_delitos_muni_mes_lag", "tasa_delitos_dep_mes_lag", "acumulado_90d", "riesgo_alto"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int if col=="riesgo_alto" else float)

    df.to_parquet(PROC_DIR / "features.parquet", index=False)
    print("✅ Features built with >20 variables (solo Santander, con lag mensual).")

if __name__ == "__main__":
    build()
