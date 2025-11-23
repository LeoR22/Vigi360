# app/services/etl.py
import argparse, pandas as pd
from app.config import RAW_DIR, PROC_DIR, SOURCES, COMMON_COLS
from pathlib import Path

def fetch_source(name: str, url: str) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.csv"
    df_iter = pd.read_csv(url, chunksize=100_000, dtype=str)
    with open(path, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(df_iter):
            mode = "w" if i == 0 else "a"
            chunk.to_csv(f, index=False, header=(i==0))
    return path

def normalize(name: str, path: Path) -> Path:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(path, dtype=str)
    # Harmonize columns
    if name == "sexuales":
        df["tipo_delito"] = "delitos_sexuales"
        keep = COMMON_COLS + ["delito"]
    elif name == "intrafamiliar":
        df["tipo_delito"] = "violencia_intrafamiliar"
        df["delito"] = "violencia_intrafamiliar"
        keep = COMMON_COLS + ["delito"]
    else:
        df["tipo_delito"] = "hurto"
        keep = COMMON_COLS + ["tipo_de_hurto"]
        df.rename(columns={"tipo_de_hurto":"modalidad_hurto"}, inplace=True)
        keep = COMMON_COLS + ["modalidad_hurto"]

    # Basic cleaning
    df = df[[c for c in df.columns if c in set(keep + ["tipo_delito"])]].copy()
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce").fillna(0).astype(int)
    df["fecha_hecho"] = pd.to_datetime(df["fecha_hecho"], errors="coerce")
    df["departamento"] = df["departamento"].str.strip().str.upper()
    df["municipio"] = df["municipio"].str.strip().str.upper()
    df["genero"] = df.get("genero","SIN_DATO").fillna("SIN_DATO").str.upper()
    df["grupo_etario"] = df.get("grupo_etario","SIN_DATO").fillna("SIN_DATO").str.upper()

    out = PROC_DIR / f"{name}.parquet"
    df.to_parquet(out, index=False)
    return out

def build_master() -> Path:
    parts = []
    for name, url in SOURCES.items():
        csv_path = fetch_source(name, url)
        pq_path = normalize(name, csv_path)
        parts.append(pd.read_parquet(pq_path))
    master = pd.concat(parts, ignore_index=True)
    # Add canonical columns
    master["anio"] = master["fecha_hecho"].dt.year
    master["mes"] = master["fecha_hecho"].dt.month
    master["dia"] = master["fecha_hecho"].dt.day
    master["dia_semana"] = master["fecha_hecho"].dt.day_name()
    master["franja_hora"] = master["fecha_hecho"].dt.hour.apply(
        lambda h: "NOCHE" if h>=19 or h<6 else ("TARDE" if h>=12 else "MAÑANA")
    )
    # Coverage flags
    master["has_edad"] = (master["grupo_etario"]!="SIN_DATO").astype(int)
    master["has_genero"] = (master["genero"]!="SIN_DATO").astype(int)
    master["has_armas"] = master["armas_medios"].notna().astype(int)
    out = PROC_DIR / "master.parquet"
    master.to_parquet(out, index=False)
    return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    if args.fetch:
        build_master()
