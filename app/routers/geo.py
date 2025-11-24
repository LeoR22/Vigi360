# app/routers/geo.py
from fastapi import APIRouter
import pandas as pd
from app.config import PROC_DIR
from app.models.schemas import GeoIncident

router = APIRouter(prefix="/geo", tags=["geo"])

_df = None

def _load():
    global _df
    if _df is None:
        _df = pd.read_parquet(PROC_DIR / "master.parquet")
        _df = _df[_df["departamento"] == "SANTANDER"].copy()

@router.get("/incidents", response_model=list[GeoIncident])
def incidents():
    _load()
    df = _df.sort_values("fecha_hecho", ascending=False).head(100).reset_index(drop=True)
    incidents = []
    # Coordenadas simuladas y severidad simple
    for i, r in df.iterrows():
        incidents.append(GeoIncident(
            lat=7.13 + (i % 50) * 0.001,
            lon=-73.13 - (i % 50) * 0.001,
            severidad="crítica" if (r.get("cantidad", 0) or 0) >= 3 else ("alta" if (r.get("cantidad", 0) or 0) == 2 else "media"),
            estado="En Atención",
            municipio=str(r.get("municipio", ""))
        ))
    return incidents
