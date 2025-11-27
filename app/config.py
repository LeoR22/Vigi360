# app/config.py
from pathlib import Path
import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar archivo .env desde la carpeta app
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Variables del .env
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")              # Azure AI Inference
OPENAI_EMBEDDINGS_URL = os.getenv("OPENAI_EMBEDDINGS_URL")  # GitHub Models endpoint
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN no está configurado en el archivo .env")

# Modelo que vas a usar
MODEL_NAME = "openai/gpt-4o"

# Cliente OpenAI apuntando al endpoint de GitHub Models
client = OpenAI(base_url=OPENAI_EMBEDDINGS_URL, api_key=GITHUB_TOKEN)

DATA_DIR = Path(__file__).resolve().parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = DATA_DIR / "logs"
GEO_DIR = DATA_DIR / "geo"

SOURCES = {
    "sexuales": "https://www.datos.gov.co/resource/fpe5-yrmw.csv?$limit=500000",
    "intrafamiliar": "https://www.datos.gov.co/resource/vuyt-mqpw.csv?$limit=800000",
    "hurtos": "https://www.datos.gov.co/resource/d4fr-sbn2.csv?$limit=100000",
}
COMMON_COLS = [
    "departamento","municipio","codigo_dane","armas_medios","fecha_hecho",
    "genero","grupo_etario","cantidad"
]
