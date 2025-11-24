# app/services/etl.py
import argparse
import pandas as pd
from pathlib import Path
from app.config import RAW_DIR, PROC_DIR, SOURCES, COMMON_COLS

# Importar los demás servicios
from app.services import features, train, validate

def fetch_source(name: str, url: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.csv"
    print(f"➡️ Descargando fuente: {name} desde {url}")
    df_iter = pd.read_csv(url, chunksize=100_000, dtype=str)
    with open(path, "w", encoding="utf-8", newline="") as f:
        for i, chunk in enumerate(df_iter):
            chunk.to_csv(f, index=False, header=(i == 0))
    print(f"✅ Fuente {name} guardada en {path}")
    return path

def normalize(name: str, path: Path) -> Path:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    print(f"➡️ Normalizando dataset: {name}")
    df = pd.read_csv(path, dtype=str)

    if name == "sexuales":
        df["tipo_delito"] = "delitos_sexuales"
        keep = COMMON_COLS + ["delito"]
    elif name == "intrafamiliar":
        df["tipo_delito"] = "violencia_intrafamiliar"
        df["delito"] = "violencia_intrafamiliar"
        keep = COMMON_COLS + ["delito"]
    else:
        df["tipo_delito"] = "hurto"
        df.rename(columns={"tipo_de_hurto": "modalidad_hurto"}, inplace=True)
        keep = COMMON_COLS + ["modalidad_hurto"]

    # Asegurar que municipio siempre exista
    if "municipio" not in df.columns:
        df["municipio"] = "SIN_DATO"

    # Filtrar columnas relevantes
    df = df[[c for c in df.columns if c in set(keep + ["tipo_delito","municipio","departamento"])]].copy()

    # Limpieza básica
    df["cantidad"] = pd.to_numeric(df.get("cantidad", 0), errors="coerce").fillna(0).astype(int)
    df["fecha_hecho"] = pd.to_datetime(df.get("fecha_hecho"), errors="coerce", dayfirst=True)

    df["departamento"] = df.get("departamento", "SIN_DATO").str.strip().str.upper()
    df["municipio"] = df.get("municipio", "SIN_DATO").str.strip().str.upper()
    df["genero"] = df.get("genero", "SIN_DATO").fillna("SIN_DATO").str.upper()
    df["grupo_etario"] = df.get("grupo_etario", "SIN_DATO").fillna("SIN_DATO").str.upper()

    # Filtro por Santander
    if "departamento" in df.columns:
        df = df[df["departamento"] == "SANTANDER"]

    out = PROC_DIR / f"{name}.parquet"
    df.to_parquet(out, index=False)
    print(f"✅ Dataset {name} normalizado y guardado en {out}")
    return out

def build_master() -> Path:
    print("➡️ Construyendo master.parquet…")
    parts = []
    for name, url in SOURCES.items():
        csv_path = fetch_source(name, url)
        pq_path = normalize(name, csv_path)
        parts.append(pd.read_parquet(pq_path))

    master = pd.concat(parts, ignore_index=True)

    # Columnas derivadas
    master["anio"] = master["fecha_hecho"].dt.year
    master["mes"] = master["fecha_hecho"].dt.month
    master["dia"] = master["fecha_hecho"].dt.day
    master["dia_semana"] = master["fecha_hecho"].dt.day_name()
    master["franja_hora"] = master["fecha_hecho"].dt.hour.apply(
        lambda h: "NOCHE" if h >= 19 or h < 6 else ("TARDE" if h >= 12 else "MAÑANA")
    )

    # Coverage flags
    master["has_edad"] = (master["grupo_etario"] != "SIN_DATO").astype(int)
    master["has_genero"] = (master["genero"] != "SIN_DATO").astype(int)
    master["has_armas"] = master.get("armas_medios", pd.Series([None]*len(master))).notna().astype(int)

    out = PROC_DIR / "master.parquet"
    master.to_parquet(out, index=False)
    print("✅ ETL terminado, master.parquet generado.")
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        # 1. ETL
        build_master()
        # 2. Features
        print("➡️ Generando features.parquet…")
        features.build()
        # 3. Train
        print("➡️ Entrenando modelo…")
        train.train_model()
        # 4. Validate
        print("➡️ Validando modelo…")
        validate.validate()
        print("🎯 Pipeline completo ejecutado con éxito.")
