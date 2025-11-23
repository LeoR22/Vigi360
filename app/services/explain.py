# app/services/explain.py
import shap, joblib, pandas as pd
from app.config import MODELS_DIR, PROC_DIR

def explain_sample(n=1000):
    model = joblib.load(MODELS_DIR / "risk_model.pkl")
    df = pd.read_parquet(PROC_DIR / "features.parquet")
    agg = df.groupby(["departamento","municipio","anio","mes"], as_index=False).agg({
        "tasa_delitos_muni_mes":"mean","tasa_delitos_dep_mes":"mean","acumulado_90d":"mean"
    })
    X = agg[["departamento","municipio","anio","mes","tasa_delitos_muni_mes","tasa_delitos_dep_mes","acumulado_90d"]].head(n)
    explainer = shap.Explainer(model.named_steps["clf"])
    # Use the transformed matrix for SHAP
    X_trans = model.named_steps["pre"].transform(X)
    shap_values = explainer(X_trans)
    return shap_values, X
