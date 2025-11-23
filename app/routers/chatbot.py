# app/routers/chatbot.py
from fastapi import APIRouter
from app.models.schemas import ChatRequest
import pandas as pd
from app.config import PROC_DIR

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

def make_response(pregunta: str, municipio: str | None, delito: str | None):
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    if municipio: df = df[df["municipio"]==municipio.upper()]
    if delito: df = df[df["tipo_delito"]==delito.upper()]
    # Simple NLG
    total = int(df["cantidad"].sum())
    top_hora = df.groupby("franja_hora")["cantidad"].sum().sort_values(ascending=False).head(1)
    hora = top_hora.index[0] if len(top_hora) else "SIN_DATO"
    top_muni = df.groupby("municipio")["cantidad"].sum().sort_values(ascending=False).head(3).index.tolist()
    reco = [
        f"Evita desplazarte en {hora.lower()} en zonas de alta concentración.",
        "Usa rutas iluminadas y comparte itinerarios con familiares.",
        "Reporta incidentes por canales oficiales."
    ]
    return f"Se registran {total} eventos{' en ' + municipio if municipio else ''}. La franja con mayor riesgo es {hora}. Municipios críticos: {', '.join(top_muni)}. Recomendaciones: " + "; ".join(reco)

@router.post("/ask")
def ask(req: ChatRequest):
    answer = make_response(req.pregunta, req.municipio, req.delito)
    return {"answer": answer}
