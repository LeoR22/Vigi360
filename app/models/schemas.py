# app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List

class CrimeQuery(BaseModel):
    departamento: Optional[str] = None
    municipio: Optional[str] = None
    tipo_delito: Optional[str] = None
    modalidad: Optional[str] = None
    anio: Optional[int] = None
    mes: Optional[int] = None
    limit: int = 500

class RiskScore(BaseModel):
    departamento: str
    municipio: str
    anio: int
    mes: int
    prob_riesgo: float
    riesgo_alto: int

class Metrics(BaseModel):
    auc: float
    f1: float
    precision: float
    recall: float
    n_train: int
    n_test: int

class ChatRequest(BaseModel):
    pregunta: str
    municipio: Optional[str] = None
    delito: Optional[str] = None
