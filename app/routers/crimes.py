# app/routers/crimes.py
from fastapi import APIRouter
import pandas as pd
from app.config import PROC_DIR
from app.models.schemas import CrimeQuery, CrimeRecord, CrimeRecentRecord

router = APIRouter(prefix="/crimes", tags=["crimes"])

_df = None

def _load_data():
    global _df
    if _df is None:
        _df = pd.read_parquet(PROC_DIR / "master.parquet")
        _df = _df[_df["departamento"] == "SANTANDER"].copy()
        _df["fecha_hecho"] = pd.to_datetime(_df["fecha_hecho"], errors="coerce")

@router.get("/recent", response_model=list[CrimeRecentRecord])
def recent():
    _load_data()
    df = _df.sort_values("fecha_hecho", ascending=False).head(100)
    out = []
    for i, r in df.iterrows():
        out.append(CrimeRecentRecord(
            id=f"#{i:03d}",
            tipo=str(r.get("tipo_delito", "OTRO")),
            descripcion = f"Reporte reciente de {r.get('delito')}",
            ubicacion=f"{str(r.get('municipio',''))}, {str(r.get('departamento',''))}",
            fecha=str(r["fecha_hecho"]),
            severidad="crítica" if (r.get("cantidad", 0) or 0) >= 3 else ("alta" if (r.get("cantidad", 0) or 0) == 2 else "media"),
            estado="En Atención"
        ))
    return out

@router.post("/query", response_model=list[CrimeRecord])
def query(payload: CrimeQuery):
    _load_data()
    df = _df.copy()
    filt = (df["departamento"] == payload.departamento)
    if payload.municipio and "municipio" in df.columns:
        filt &= (df["municipio"] == payload.municipio)
    if payload.tipo_delito and "tipo_delito" in df.columns:
        filt &= (df["tipo_delito"] == payload.tipo_delito)
    if payload.anio:
        filt &= (df["anio"] == payload.anio)
    if payload.mes:
        filt &= (df["mes"] == payload.mes)

    df = df.loc[filt, ["departamento","municipio","fecha_hecho","tipo_delito","cantidad"]].sort_values("fecha_hecho", ascending=False).head(payload.limit)
    df["fecha_hecho"] = df["fecha_hecho"].astype(str)
    return [CrimeRecord(**r) for r in df.to_dict(orient="records")]
