# app/routers/geo.py
from fastapi import APIRouter
import pandas as pd
from app.config import PROC_DIR, GEO_DIR
from app.models.schemas import GeoIncident

router = APIRouter(prefix="/geo", tags=["geo"])

_df = None
_geo = None

def _load():
    global _df, _geo
    if _df is None:
        _df = pd.read_parquet(PROC_DIR / "master.parquet")
        _df = _df[_df["departamento"] == "SANTANDER"].copy()
    if _geo is None:
        _geo = pd.read_csv(GEO_DIR / "municipios.csv") 

@router.get("/incidents", response_model=list[GeoIncident])
def incidents():
    _load()
    df = _df.sort_values("fecha_hecho", ascending=False).head(200).reset_index(drop=True)

    df["codigo_dane"] = df["codigo_dane"].astype(str)
    _geo["codigo_dane"] = _geo["codigo_dane"].astype(str)
    df = df.merge(_geo, on="codigo_dane", how="left")  
    incidents = []
    for _, r in df.iterrows():
        incidents.append(GeoIncident(
            lat=float(r.get("lat", 0)),
            lon=float(r.get("lon", 0)),
            severidad="crítica" if (r.get("cantidad", 0) or 0) >= 3 else ("alta" if (r.get("cantidad", 0) or 0) == 2 else "media"),
            estado="En Atención",
            municipio=str(r.get("municipio", ""))
        ))
    return incidents