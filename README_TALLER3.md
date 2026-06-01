# 🩺 Pipeline MLOps — Diagnóstico Clínico (Reestructuración Semanas 5-6)

**Equipo:** RM · Tavo · Juanse  
**Curso:** MLOps — MIIA · ICESI · 2026  
**Repo Taller 1 (base):** [diagnostico-medico_RM-Tavo-Juanse-mlops-U2](https://github.com/juanseo/diagnostico-medico_RM-Tavo-Juanse-mlops-U2)

---

## Descripción del problema

En entornos clínicos, la evaluación rápida del estado de salud de un paciente es crítica. Se requiere un modelo capaz de predecir, dados síntomas fisiológicos básicos, si un paciente sufre alguna enfermedad. El reto es doble: enfermedades comunes cuentan con muchos datos, mientras que las enfermedades **huérfanas** tienen datos escasos.

El sistema clasifica a un paciente en cinco estados: `NO ENFERMO`, `ENFERMEDAD LEVE`, `ENFERMEDAD AGUDA`, `ENFERMEDAD CRÓNICA`, `ENFERMEDAD TERMINAL`.

---

## Diagrama General del Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE MLOps                               │
│                  Diagnóstico Clínico v2.0                           │
└─────────────────────────────────────────────────────────────────────┘

 ┌──────────────┐
 │  1. DISEÑO   │ GitHub (docs), Great Expectations (restricciones de datos)
 └──────┬───────┘
        │
 ┌──────▼────────────────────────┐
 │  2. INGESTA Y PREPROCESAMIENTO│ Apache Airflow + DVC + Pandas + Great Expectations
 └──────┬────────────────────────┘
        │
 ┌──────▼──────────────┐
 │  3. FEATURE STORE   │ Feast (features reutilizables entre experimentos)
 └──────┬──────────────┘
        │
 ┌──────▼─────────────────────────────────────────┐
 │  4. DESARROLLO DEL MODELO                      │
 │   ├── Enf. comunes  → PyCaret + scikit-learn   │
 │   ├── Enf. huérfanas → few-shot (learn2learn)  │
 │   ├── Tracking      → MLflow                   │
 │   └── Testing       → pytest                   │
 └──────┬─────────────────────────────────────────┘
        │
 ┌──────▼───────────────────────────────────┐
 │  5. SOURCE REPOSITORY & CI/CD            │ GitHub + GitHub Actions + Docker
 └──────┬───────────────────────────────────┘
        │
 ┌──────▼──────────────────────────────────────────┐
 │  6. DESPLIEGUE                                  │
 │   ├── Local  → Docker run (Flask en localhost)  │
 │   └── Nube   → Azure Container Registry / AWS  │
 └──────┬──────────────────────────────────────────┘
        │
 ┌──────▼──────────────────────────────────────────┐
 │  7. MONITOREO Y RE-ENTRENAMIENTO                │
 │   ├── Model drift   → Evidently AI              │
 │   ├── Infra         → Sentry                    │
 │   ├── Alertas       → Fiddler / Airflow         │
 │   └── Re-train loop → Apache Airflow            │
 └─────────────────────────────────────────────────┘
        ↑___________________________________________│
                    (feedback loop)
```

---

## Etapas del Pipeline — Detalle

### Etapa 1 — Diseño del Sistema

**Objetivo:** Definir el problema, restricciones y métricas de éxito antes de escribir una línea de código.

**Tecnologías:**
- **GitHub** (control de versiones de código y documentación del problema)
- **Great Expectations** (perfil inicial de calidad de datos esperada)

**Suposiciones:**
- Los datos de entrada son variables fisiológicas tabulares (temperatura, frecuencia cardíaca, nivel de dolor). No se trabaja con imágenes ni texto libre.
- Existe regulación de privacidad aplicable (equivalente a HIPAA/GDPR) que impide compartir datos entre instituciones sin anonimización.
- Para enfermedades comunes se asume disponibilidad de más de 1 000 ejemplos etiquetados; para enfermedades huérfanas, menos de 100.
- La métrica principal es **Recall** (minimizar falsos negativos en diagnóstico), con umbral mínimo aceptable de 0.75.
- El médico puede correr la solución localmente si el cómputo es bajo, o hacer peticiones a una API si el modelo vive en la nube.

**Restricciones clave:**
- Datos huérfanos escasos → se requiere técnicas de pocos ejemplos.
- Privacidad → los datos no deben salir de la institución en crudo.
- Tiempo de inferencia < 2 segundos por paciente (requisito de uso clínico).

---

### Etapa 2 — Ingesta y Preprocesamiento de Datos

**Objetivo:** Recolectar, limpiar y versionar los datos de manera reproducible y automatizada.

**Tecnologías:**
- **Apache Airflow** — orquestación del pipeline de ingesta (DAGs programables). Justificación: visto en Sesión 5, usado en casos reales de monitoreo en producción (Airflow + Snowflake + QuickSight).
- **DVC (Data Version Control)** — versionamiento de datasets. Justificación: el material del curso (Sesión 4) referencia repos de ejemplo con versionamiento; DVC es el estándar de la industria para esto en MLOps.
- **Pandas** — transformaciones y limpieza de datos tabulares.
- **Great Expectations** — validación automática de esquema y rangos (e.g., temperatura fuera de 30–45°C → alerta).

**Suposiciones:**
- Los datos clínicos provienen de un sistema de Historia Clínica Electrónica (HCE) exportado en CSV/JSON semanalmente.
- El pipeline de ingesta corre cada domingo a las 2:00 AM mediante un DAG de Airflow.
- Los datos nuevos se versionar con DVC antes de usarse en re-entrenamiento.
- Se asume que los datos ya tienen etiquetas asignadas por médicos especialistas.
- Para enfermedades huérfanas, los datos provienen de bases como Orphanet y ClinVar (acceso público).

**Proceso:**
1. Airflow extrae CSV del HCE.
2. Great Expectations valida rangos y ausencia de nulos.
3. Pandas realiza normalización y codificación.
4. DVC versiona el dataset limpio con hash reproducible.
5. Dataset queda disponible para la Feature Store.

---

### Etapa 3 — Feature Store

**Objetivo:** Centralizar las features procesadas para que puedan reutilizarse en entrenamiento, evaluación y serving sin duplicar transformaciones.

**Tecnologías:**
- **Feast** — Feature Store open-source. Justificación: mencionado en Sesión 6 como herramienta clave del stack MLOps junto a MLflow y Kubeflow.

**Suposiciones:**
- Las features son estables (temperatura, frecuencia cardíaca, nivel de dolor) y no cambian en el corto plazo.
- La Feature Store actúa como intermediario entre el pipeline de datos y el pipeline de entrenamiento.
- Para el MVP (versión actual de la solución), la Feature Store es una tabla versionada por DVC; Feast se incorpora en producción real.

---

### Etapa 4 — Desarrollo del Modelo

**Objetivo:** Entrenar, evaluar y registrar modelos para enfermedades comunes y huérfanas.

**Tecnologías:**

| Subtarea | Tecnología | Justificación (sesión del curso) |
|---|---|---|
| Enfermedades comunes | **PyCaret** | Sesión 4: el profesor provee repo `avila196/sample-pycaret` como ejemplo de pipeline de ML. Permite AutoML rápido sobre datos tabulares. |
| Enfermedades huérfanas | **PyTorch + learn2learn** | Sesión 1: se menciona explícitamente few-shot y meta-learning para datos escasos. learn2learn implementa MAML y Prototypical Networks sobre PyTorch. |
| Experiment tracking | **MLflow** | Sesión 5 y 6: MLflow aparece como herramienta central de tracking y model registry tanto en MLOps como en LLMOps. |
| Testing del modelo | **pytest** | Ya implementado en el repo actual (`test_app.py`). Corre automáticamente en GitHub Actions. |
| Validación clínica | **Cross-validation k-fold** + Recall, F1, AUC-ROC | Sesión 5: se mencionan estas métricas explícitamente. Recall es la métrica principal para minimizar falsos negativos. |

**Suposiciones:**
- Para enfermedades comunes: clasificador tabulado con PyCaret (RandomForest, XGBoost, LogReg comparados automáticamente). El mejor modelo se registra en MLflow.
- Para enfermedades huérfanas: modelo few-shot con PyTorch entrenado sobre los pocos casos disponibles. Validado con médicos especialistas.
- El umbral de producción es Recall ≥ 0.75. Si un modelo no lo alcanza, no se publica.
- MLflow Model Registry tiene tres etapas: `Staging → Production → Archived`.
- La función `predecir_enfermedad()` actual (umbrales estáticos) es el baseline de referencia.

**Flujo de experimentación:**
```
PyCaret.compare_models() → Mejor modelo → mlflow.log_model() → Model Registry (Staging)
                                                     ↓
                                          Validación médica + Recall ≥ 0.75
                                                     ↓
                                          mlflow.transition_model_version_stage("Production")
```

---

### Etapa 5 — Source Repository y CI/CD

**Objetivo:** Garantizar que cada cambio en el código pase por pruebas automáticas, construcción de imagen y publicación del contenedor.

**Tecnologías:**
- **GitHub** — control de versiones, branches por feature, Pull Requests.
- **GitHub Actions** — CI/CD pipeline automático. Ya implementado en `.github/workflows/ci-cd.yml`.
- **Docker** — contenerización del servicio Flask. Ya implementado con `Dockerfile`.
- **GitHub Container Registry (GHCR)** — publicación de imágenes Docker. Alternativa: Azure Container Registry (mencionado en Sesión 4).

**Suposiciones:**
- El flujo de ramas sigue el modelo trunk-based: `feature/* → main` con PRs.
- Cada PR dispara: (1) lint, (2) tests con pytest, (3) build de imagen Docker, (4) push a GHCR solo si todos pasan.
- La imagen de producción se etiqueta con la versión semántica (`v1.x.x`).

**Flujo CI/CD actual (ya implementado):**
```
Push a main
  → GitHub Actions: pytest test_app.py
  → GitHub Actions: docker build
  → GitHub Actions: docker push ghcr.io/juanseo/diagnostico-medico
```

**Justificación de tecnologías:** Sesión 4 del curso detalla explícitamente el uso de GitHub Actions para build, test y push de imágenes Docker hacia Azure Container Registry y AWS ECR, con tutoriales de referencia provistos por el profesor.

---

### Etapa 6 — Despliegue

**Objetivo:** Poner el modelo a disposición del médico de forma reproducible, ya sea local o en la nube.

**Tecnologías:**
- **Flask** — servidor API REST + interfaz web. Ya implementado en `app.py`.
- **Docker** — portabilidad total. El médico solo necesita Docker instalado.
- **Azure Container Registry / AWS ECR** — registro de imágenes para despliegue en nube (Sesión 4).

**Dos modos de despliegue (según restricción del taller):**

| Modo | Cuándo usarlo | Comando |
|---|---|---|
| **Local** | Recursos bajos, datos sensibles que no deben salir | `docker run -p 5000:5000 ghcr.io/juanseo/diagnostico-medico` |
| **Nube (API)** | Múltiples médicos, alta disponibilidad | Deploy en Azure App Service / AWS ECS |

**Suposiciones:**
- El modo local es el default para el MVP. La imagen Docker es self-contained.
- El modelo de ML se empaqueta dentro de la imagen (archivo `.pkl` generado por PyCaret/MLflow).
- En nube, el endpoint es `POST /predecir` sobre HTTPS con autenticación básica.
- El despliegue en nube es CD automático desde GitHub Actions al aprobar un PR en `main`.

---

### Etapa 7 — Monitoreo y Re-entrenamiento

**Objetivo:** Detectar degradación del modelo en producción y disparar re-entrenamiento de forma automatizada.

**Tecnologías:**

| Subtarea | Tecnología | Justificación (sesión del curso) |
|---|---|---|
| Data drift y model drift | **Evidently AI** | Sesión 5: el profesor usa Evidently AI explícitamente para detectar covariate shifts y concept shifts. |
| Infra monitoring | **Sentry** | Sesión 5: mencionado como herramienta de monitoreo de infraestructura (downtimes, latencia, bugs). |
| Alertas del modelo | **Fiddler** | Sesión 5: el profesor muestra Fiddler en el caso real de credit risk models para alertas por métricas. |
| Orquestación re-entrenamiento | **Apache Airflow** | Sesión 5: caso real "Airflow + Snowflake + QuickSight" para pipeline de monitoreo. |
| Model Registry | **MLflow** | Sesión 5 y 6: gestión de versiones del modelo con etapas Staging → Production. |

**Suposiciones:**
- Evidently AI corre semanalmente comparando la distribución de los síntomas recibidos vs. la distribución de entrenamiento.
- Un **covariate shift** en temperatura > 2 desviaciones estándar dispara alerta.
- Un **concept shift** (degradación del Recall < 0.75 en nuevos datos etiquetados) dispara re-entrenamiento.
- El re-entrenamiento es un DAG de Airflow que reutiliza la Etapa 2→4 completa.
- Sentry monitorea la disponibilidad del servicio Flask (uptime, latencia de respuesta).
- Los resultados de monitoreo se persisten en una base de datos ligera (SQLite o DuckDB, como se menciona en Sesión 5).

**Trigger de re-entrenamiento:**
```
Evidently AI detecta drift
  → Airflow dispara DAG "retrain_pipeline"
  → Ingesta nueva data (Etapa 2)
  → Re-entrenamiento PyCaret/PyTorch (Etapa 4)
  → Validación Recall ≥ 0.75
  → MLflow: nuevo modelo a Staging
  → Aprobación manual → Production
```

---

## Stack Tecnológico Completo

| Etapa | Tecnología | Tipo |
|---|---|---|
| Control de versiones | **GitHub** | SCM |
| Orquestación de datos | **Apache Airflow** | Orquestador |
| Versionamiento de datos | **DVC** | Data versioning |
| Validación de datos | **Great Expectations** | Data quality |
| Transformaciones | **Pandas** | Processing |
| Feature Store | **Feast** | Feature management |
| Modelo comunes | **PyCaret + scikit-learn** | AutoML |
| Modelo huérfanas | **PyTorch + learn2learn** | Few-shot learning |
| Experiment tracking | **MLflow** | Tracking + Registry |
| Testing | **pytest** | Unit testing |
| CI/CD | **GitHub Actions** | Automation |
| Contenerización | **Docker** | Packaging |
| Container Registry | **GitHub Container Registry** | Image registry |
| Serving | **Flask** | API REST |
| Data drift | **Evidently AI** | Monitoring |
| Infra monitoring | **Sentry** | Observability |
| Alertas | **Fiddler** | Alerting |
| Re-entrenamiento | **Apache Airflow** | Orchestration |

---

## Instrucciones de uso (versión actual — MVP)

```bash
# Construir la imagen
docker build -t diagnostico-medico .

# Ejecutar el servicio
docker run -p 5000:5000 diagnostico-medico

# Acceder en el navegador
http://localhost:5000

# API REST
curl -X POST http://localhost:5000/predecir \
     -H "Content-Type: application/json" \
     -d '{"temperatura": 38.5, "frecuencia_cardiaca": 110, "nivel_dolor": 6}'
```

---

## Estructura del repositorio

```
diagnostico-medico_RM-Tavo-Juanse-mlops-U2/
├── .github/workflows/
│   └── ci-cd.yml              # Pipeline CI/CD: test → build → push
├── templates/
│   └── index.html             # Interfaz web del médico
├── Dockerfile                 # Imagen Docker (python:3.11-slim + Flask)
├── app.py                     # API REST + función predecir_enfermedad()
├── test_app.py                # Pruebas unitarias (pytest)
├── requirements.txt           # Dependencias Python
├── README.md                  # Solución Unidad 1 (base)
├── README_TALLER3.md          # Este archivo — Pipeline reestructurado
└── CHANGELOG.md               # Registro de cambios vs. propuesta inicial
```

---

*Proyecto educativo — MIIA MLOps · ICESI · 2026*
