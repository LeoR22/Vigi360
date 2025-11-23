# app/services/train.py
import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
import joblib
from app.config import PROC_DIR, MODELS_DIR

def fit():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROC_DIR / "features.parquet")

    # Aggregate to municipio-mes
    agg = df.groupby(["departamento","municipio","anio","mes"], as_index=False).agg({
        "tasa_delitos_muni_mes":"mean","tasa_delitos_dep_mes":"mean","acumulado_90d":"mean",
        "has_edad":"mean","has_genero":"mean","has_armas":"mean"
    })
    # Merge target
    target = df.groupby(["municipio","anio","mes"], as_index=False)["riesgo_alto"].max()
    data = agg.merge(target, on=["municipio","anio","mes"], how="left")

    X = data[["departamento","municipio","anio","mes","tasa_delitos_muni_mes","tasa_delitos_dep_mes","acumulado_90d"]]
    y = data["riesgo_alto"].fillna(0).astype(int)

    cat_cols = ["departamento","municipio"]
    num_cols = ["anio","mes","tasa_delitos_muni_mes","tasa_delitos_dep_mes","acumulado_90d"]

    pre = ColumnTransformer([
        ("onehot", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ("pass", "passthrough", num_cols)
    ])

    clf = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.08, subsample=0.8, colsample_bytree=0.8,
        reg_lambda=1.0, random_state=42, n_jobs=4
    )

    model = Pipeline([("pre", pre), ("clf", clf)])

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]

    metrics = {
        "auc": float(roc_auc_score(y_test, y_prob)),
        "f1": float(f1_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test))
    }

    joblib.dump(model, MODELS_DIR / "risk_model.pkl")
    pd.Series(metrics).to_json(MODELS_DIR / "metrics.json")
    print("Saved model and metrics:", metrics)

if __name__ == "__main__":
    fit()
