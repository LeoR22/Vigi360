# app/config.py
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = DATA_DIR / "logs"

SOURCES = {
    "sexuales": "https://www.datos.gov.co/resource/fpe5-yrmw.csv?$limit=500000",
    "intrafamiliar": "https://www.datos.gov.co/resource/vuyt-mqpw.csv?$limit=800000",
    "hurtos": "https://www.datos.gov.co/resource/d4fr-sbn2.csv?$limit=100000",
}
COMMON_COLS = [
    "departamento","municipio","codigo_dane","armas_medios","fecha_hecho",
    "genero","grupo_etario","cantidad"
]
