# app/services/validate.py
import joblib
import pandas as pd
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve, auc
from app.config import MODELS_DIR, PROC_DIR

def validate():
    # Cargar modelo entrenado
    model = joblib.load(MODELS_DIR / "risk_model.pkl")

    # Cargar features y filtrar solo Santander
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    df = df[df["departamento"] == "SANTANDER"].copy()

    # Usar último año como validación externa
    ultimo_anio = int(df["anio"].max())
    val_df = df[df["anio"] == ultimo_anio]

    # Features consistentes con train.py (usando columnas con lag)
    X_val = val_df[[
    "departamento","anio","mes",
    "tasa_delitos_muni_mes_lag","tasa_delitos_dep_mes_lag","acumulado_90d"
    ]]

    y_val = val_df["riesgo_alto"]

    # Predicciones
    y_pred = model.predict(X_val)
    print("📊 Validación externa (último año):")
    print(classification_report(y_val, y_pred))

    # Métricas adicionales
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_val)[:, 1]
        roc = roc_auc_score(y_val, y_proba)
        precision, recall, _ = precision_recall_curve(y_val, y_proba)
        pr = auc(recall, precision)
        print(f"ROC-AUC: {roc:.3f}")
        print(f"PR-AUC: {pr:.3f}")

if __name__ == "__main__":
    validate()
