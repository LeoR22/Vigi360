# app/routers/crimes.py
from fastapi import APIRouter
from app.models.schemas import CrimeQuery
import pandas as pd
from app.config import PROC_DIR

router = APIRouter(prefix="/crimes", tags=["crimes"])

@router.post("/query")
def query_crimes(q: CrimeQuery):
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    for field in ["departamento","municipio","anio","mes"]:
        val = getattr(q, field)
        if val is not None:
            df = df[df[field]==val]
    if q.tipo_delito:
        df = df[df["tipo_delito"]==q.tipo_delito.upper()]
    if q.modalidad:
        df = df[df["modalidad"]==q.modalidad.upper()]
    df = df[["departamento","municipio","anio","mes","cantidad","tipo_delito","modalidad","tasa_delitos_muni_mes"]]
    return {"count": int(len(df)), "items": df.head(q.limit).to_dict(orient="records")}
