# Tablero Inteligente de Seguridad Ciudadana para Santander
![Python](https://img.shields.io/badge/python-3670A0?style=flat&logo=python&logoColor=ffdd54)  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) ![React](https://shields.io/badge/-react-4377cb?logo=react)   ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)  ![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)  ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)  ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=flat&logo=numpy&logoColor=white)  ![XGBoost](https://img.shields.io/badge/xgboost-%23FF6600.svg?style=flat&logo=xgboost&logoColor=white)  ![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=flat&logo=python&logoColor=white)![SHAP](https://img.shields.io/badge/shap-%23000000.svg?style=flat&logo=python&logoColor=white) 
![Leaflet](https://img.shields.io/badge/leaflet-%23199900.svg?style=flat&logo=leaflet&logoColor=white)  


Este proyecto fue desarrollado como parte del concurso **Datos al Ecosistema 2025**, con el objetivo de mejorar la toma de decisiones institucionales y el acceso ciudadano a información crítica sobre seguridad en los municipios no certificados del departamento de Santander.



## 🧱 Arquitectura del Proyecto

```bash
santander-security/ 
├─ app/ # Backend FastAPI 
│ ├─ main.py # Punto de entrada de la API 
│ ├─ config.py # Rutas y configuración general 
│ ├─ routers/ # Endpoints organizados por dominio 
│ │ ├─ crimes.py # Consultas de delitos 
│ │ ├─ analytics.py # Predicción, métricas y visualización 
│ │ ├─ chatbot.py # Interacción comunitaria 
│ │ ├─ reports.py # Reportes ciudadanos en tiempo real (opcional) 
│ ├─ models/ # Esquemas Pydantic 
│ │ ├─ schemas.py
│ ├─ services/ # Lógica de negocio y procesamiento
│ │ ├─ etl.py # Ingesta y normalización de datos 
│ │ ├─ features.py # Derivación de variables (>25)
│ │ ├─ train.py # Entrenamiento de modelo ML 
│ │ ├─ explain.py # Explicabilidad con SHAP 
│ │ ├─ storage.py # Validación y cobertura 
│ │ ├─ chatbot.py # Generación de respuestas
│ ├─ data/
│ │ ├─ raw/ # CSV originales
│ │ ├─ processed/ # Parquet normalizados 
│ │ ├─ models/ # Modelos entrenados (*.pkl) 
│ │ ├─ logs/ # Logs de ejecución y API 
├─ scripts/ # Automatización 
│ ├─ bootstrap.sh # ETL + features + entrenamiento 
│ ├─ run_train.sh # Entrenamiento manual 
│ ├─ seed_demo.sh # Datos de prueba
├─ frontend/ # Aplicación React (mapa, filtros, chatbot) 
├─ dockerfile # Imagen backend 
├─ docker-compose.yml # Backend + Frontend 
├─ requirements.txt # Dependencias Python 
├─ README.md # Documentación del proyecto
```



## 🚀 Objetivo

Construir un tablero web inteligente que integre:
- Visualización geoespacial de delitos
- Modelos de Machine Learning explicables para predicción de riesgo
- Chatbot comunitario entrenado con datos locales

## 🧠 Datos utilizados

Se integraron más de 1 millón de registros provenientes de datos abiertos:

| Dataset | Fuente | Filas | Variables |
|--------|--------|-------|-----------|
| Delitos sexuales | [datos.gov.co](https://www.datos.gov.co/resource/fpe5-yrmw.csv) | 365K | 9 |
| Violencia intrafamiliar | [datos.gov.co](https://www.datos.gov.co/resource/vuyt-mqpw.csv) | 634K | 8 |
| Hurtos por modalidades | [datos.gov.co](https://www.datos.gov.co/resource/d4fr-sbn2.csv) | 43K | 9 |

Se derivaron más de **25 variables** adicionales para análisis predictivo, cobertura, temporalidad y riesgo.

## 🧩 Componentes

- **ETL y normalización**: limpieza, estandarización y unión de datasets
- **Feature engineering**: derivación de variables explicables
- **Modelo ML**: clasificación de riesgo alto por municipio/mes
- **API FastAPI**: endpoints para dashboard y chatbot
- **Chatbot comunitario**: respuestas preventivas basadas en datos locales

## 📊 Endpoints principales

| Endpoint | Descripción |
|---------|-------------|
| `/crimes/query` | Consulta de delitos por filtros |
| `/analytics/geo/heatmap` | Datos agregados para mapa |
| `/analytics/risk/predict` | Predicción de riesgo por municipio |
| `/analytics/metrics` | Métricas del modelo (AUC, F1, etc.) |
| `/chatbot/ask` | Preguntas ciudadanas con respuesta explicada |
|`/chatbot/quick/{tipo}` |Respuestas rápidas (estadisticas, prediccion, situacion) |
| `/reports/submit` | Reportes ciudadanos en tiempo real (opcional) |

## 🧪 Métricas del modelo

- Precisión clase 0: 0.98
- Recall clase 0: 1.00
- F1-score clase 0: 0.99
- Precisión clase 1: 1.00
- Recall clase 1: 0.99
- F1-score clase 1: 0.99
- Accuracy global: 0.99
- ROC-AUC: 1.000
- PR-AUC: 1.000
- 📌 El modelo se guarda automáticamente en:
```
app/data/models/risk_model.pkl
```
## ⚙️ Modelo, algoritmos y frameworks utilizados
Modelo principal: GradientBoostingClassifier (Scikit-learn)
- *Algoritmos:*
    - Gradient Boosting para clasificación binaria de riesgo
    - Validación temporal y externa con métricas ROC-AUC y PR-AUC
    - Feature engineering con más de 25 variables derivadas (temporales, demográficas, geoespaciales)

## Eejecución del Modelo
```
python -m app.services.etl --fetch
```
*Este comando corre todo el pipeline:*

- ETL → limpieza y normalización de datos
- Features → generación de features.parquet
- Train → entrenamiento del modelo y guardado en risk_model.pkl
- Validate → validación temporal y externa con métricas


## 🗺️ Impacto

- **Institucional**: focalización de recursos y agentes
- **Comunitario**: acceso ciudadano a información clara
- **Técnico**: IA explicable y auditable
- **Territorial**: identificación de zonas críticas

## 🧪 Cómo levantar todo
### 1. Clona el proyecto y entra al directorio
```
https://github.com/LeoR22/santander-security
```
Moverse directorio principal
```
cd santander-security
```
### 2. Ejecuta el bootstrap para preparar datos y modelo
```
scripts/bootstrap.sh
```
### 3. Levanta backend + frontend
```
docker-compose up --build
```
### Acceso Backend y Frontend
```
Accede al backend en: http://localhost:8000/docs
Accede al frontend en: http://localhost:4200
```


## 🧪 Comandos de prueba (curl)

### Consulta delitos por municipio
```bash
curl -X POST http://localhost:8000/crimes/query -H "Content-Type: application/json" -d '{"municipio":"BUCARAMANGA","tipo_delito":"HURTO"}'
```

### Predicción de riesgo
```bash
curl "http://localhost:8000/analytics/risk/predict?departamento=SANTANDER&municipio=BUCARAMANGA&anio=2025&mes=10"
```

### Métricas del modelo
```bash
curl http://localhost:8000/analytics/metrics
```

### Pregunta al chatbot
```bash
curl -X POST http://localhost:8000/chatbot/ask -H "Content-Type: application/json" -d '{"pregunta":"¿Qué tan seguro es Bucaramanga en la noche?","municipio":"BUCARAMANGA"}'
```


## 👥 Equipo
- Leandro ⚡ – Data Engineer & Backend
- Gissell Trejos – Frontend & UX

---

## Contribuciones

**Si deseas contribuir a este proyecto, sigue estos pasos:**

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature-nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Agrega nueva funcionalidad'`).
4. Sube los cambios a la rama (`git push origin feature-nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

- Leandro Rivera: <leo.232rivera@gmail.com>
- Linkedin: <https://www.linkedin.com/in/leandrorivera/>
- Gissell Trejos: <gtrejosmarin@gmail.com>
- Linkedin:  <https://www.linkedin.com/in/gisselltrejosmarin>

### ¡Feliz Codificación! 🚀


Si encuentras útil este proyecto, ¡dale una ⭐ en GitHub! 😊

