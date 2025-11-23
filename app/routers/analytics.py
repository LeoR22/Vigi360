# app/routers/analytics.py
from fastapi import APIRouter
from app.models.schemas import Metrics, RiskScore
import pandas as pd, joblib
from app.config import PROC_DIR, MODELS_DIR

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/metrics", response_model=Metrics)
def model_metrics():
    return pd.read_json(MODELS_DIR / "metrics.json", typ="series").to_dict()

@router.get("/geo/heatmap")
def geo_heatmap(departamento: str | None = None, anio: int | None = None, mes: int | None = None):
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    if departamento: df = df[df["departamento"]==departamento.upper()]
    if anio: df = df[df["anio"]==anio]
    if mes: df = df[df["mes"]==mes]
    agg = df.groupby(["departamento","municipio"], as_index=False)["cantidad"].sum()
    # Note: for actual geospatial, join with shapes/coords (DANE centroid file) before returning
    return {"items": agg.to_dict(orient="records")}

@router.get("/risk/predict")
def predict_risk(departamento: str, municipio: str, anio: int, mes: int):
    model = joblib.load(MODELS_DIR / "risk_model.pkl")
    X = pd.DataFrame([{
        "departamento": departamento.upper(), "municipio": municipio.upper(),
        "anio": anio, "mes": mes,
        "tasa_delitos_muni_mes": 0, "tasa_delitos_dep_mes": 0, "acumulado_90d": 0
    }])
    # Retrieve historical rates to fill features
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    hist = df[(df["departamento"]==departamento.upper()) & (df["municipio"]==municipio.upper())]
    if len(hist):
        last = hist.sort_values(["anio","mes"]).tail(1).iloc[0]
        X["tasa_delitos_muni_mes"] = float(last["tasa_delitos_muni_mes"])
        X["tasa_delitos_dep_mes"] = float(last["tasa_delitos_dep_mes"])
        X["acumulado_90d"] = float(last["acumulado_90d"])
    prob = float(model.predict_proba(X)[0,1])
    return RiskScore(departamento=departamento, municipio=municipio, anio=anio, mes=mes,
                     prob_riesgo=prob, riesgo_alto=int(prob>=0.5))
