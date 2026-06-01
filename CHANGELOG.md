# CHANGELOG — Pipeline MLOps Diagnóstico Clínico

Registro de cambios entre la propuesta inicial (Semanas 1-2, Taller 1) y la propuesta reestructurada (Semanas 5-6, Taller 3).

---

## [2.0.0] — 2026-05-31 — Reestructuración completa del pipeline (Taller 3)

### Added

- **Tecnologías específicas** para cada etapa del pipeline, con justificación basada en el material del curso:
  - Apache Airflow para orquestación de ingesta y re-entrenamiento (Sesión 5).
  - DVC para versionamiento reproducible de datasets.
  - Great Expectations para validación automática de calidad de datos.
  - Feast como Feature Store entre ingesta y entrenamiento.
  - PyCaret para AutoML en enfermedades comunes (Sesión 4 — repo `avila196/sample-pycaret`).
  - PyTorch + learn2learn para few-shot learning en enfermedades huérfanas (Sesión 1).
  - MLflow para experiment tracking y model registry (Sesión 5, 6).
  - Evidently AI para detección de data drift y concept drift en producción (Sesión 5).
  - Sentry para monitoring de infraestructura (Sesión 5).
  - Fiddler para sistema de alertas del modelo (Sesión 5).

- **Suposiciones explícitas** documentadas por etapa:
  - Volumen de datos: >1000 ejemplos para enfermedades comunes, <100 para huérfanas.
  - Umbral de producción: Recall ≥ 0.75.
  - Frecuencia de ingesta: DAG de Airflow corriendo cada domingo a las 2:00 AM.
  - Trigger de re-entrenamiento: covariate shift > 2σ o Recall < 0.75.
  - Modo de despliegue: local (Docker run) o nube (Azure/AWS) según recursos del médico.

- **Feature Store** (Feast) como etapa intermedia entre preprocesamiento y entrenamiento: no existía en v1.

- **Two-path model training**: separación explícita entre el camino para enfermedades comunes y el camino para enfermedades huérfanas, con tecnologías distintas para cada uno.

- **MLflow Model Registry** con estados Staging → Production → Archived, reemplazando el deploy directo a Docker.

- **Loop de re-entrenamiento automatizado** orquestado por Airflow: disparo por drift → re-ingesta → re-entrenamiento → validación → promoción a producción.

- **README_TALLER3.md** con descripción completa del pipeline reestructurado, diagrama ASCII, tabla de stack tecnológico y justificaciones.

### Changed

- **Etapa de Diseño**: en v1 era genérica (sin herramientas). En v2 incluye GitHub para documentación y Great Expectations para definir restricciones de calidad de datos desde el inicio.

- **Etapa de Ingesta**: en v1 era implícita (se mencionaban fuentes: HCE, Orphanet). En v2 es una etapa formal con Airflow como orquestador, DVC como versionador y Great Expectations como validador.

- **Etapa de Desarrollo del modelo**: en v1 se proponían modelos genéricos (XGBoost, Random Forest, few-shot) sin tecnología concreta. En v2 se especifica PyCaret para comunes y PyTorch + learn2learn para huérfanas, ambos con tracking en MLflow.

- **Etapa de Despliegue**: en v1 se mencionaba Docker + API REST de forma general. En v2 se especifican dos modos (local vs. nube), el flujo de CI/CD con GitHub Actions y el uso de GitHub Container Registry para publicación de imágenes.

- **Etapa de Monitoreo**: en v1 se mencionaba "data drift, model drift, Evidently AI" como conceptos. En v2 cada herramienta tiene un rol concreto (Evidently AI para drift, Sentry para infra, Fiddler para alertas, Airflow para trigger de re-entrenamiento) con umbrales definidos.

### Kept (de v1 a v2 sin cambios)

- **Flask** como framework de serving (ya implementado en `app.py`).
- **Docker** como tecnología de empaquetado (ya implementado con `Dockerfile`).
- **GitHub Actions** como motor de CI/CD (ya implementado en `.github/workflows/ci-cd.yml`).
- **pytest** para pruebas unitarias (ya implementado en `test_app.py`).
- **Interfaz web** con formulario para el médico (ya implementada en `templates/index.html`).
- Los **5 estados de diagnóstico**: NO ENFERMO, ENFERMEDAD LEVE, ENFERMEDAD AGUDA, ENFERMEDAD CRÓNICA, ENFERMEDAD TERMINAL.
- Los **3 parámetros de entrada**: temperatura, frecuencia cardíaca, nivel de dolor.

### Removed / Deprecated

- La propuesta en v1 no especificaba tecnologías para ingesta ni para monitoring, por lo que esas secciones eran descripciones conceptuales. En v2 se reemplazan por etapas técnicas concretas.

---

## [1.0.0] — 2026-05-13 — Propuesta inicial del pipeline (Taller 1)

### Summary

Primera propuesta del pipeline end-to-end para el problema de diagnóstico clínico. Incluía:

- Diagrama con 5 fases: Diseño → Ingesta y Preprocesamiento → Desarrollo del Modelo → Despliegue → Monitoreo y Re-entrenamiento.
- Descripción general de tecnologías posibles sin especificar stack concreto.
- Función simulada `predecir_enfermedad()` con umbrales estáticos (sin modelo ML real).
- Servicio Flask contenerizado con Docker.
- Interfaz web para el médico.
- API REST `POST /predecir`.
- Cuatro estados diagnósticos (sin ENFERMEDAD TERMINAL).

### Limitaciones identificadas (motivaron la reestructuración)

- No se especificaban tecnologías concretas para ninguna etapa.
- No se definían suposiciones formales (volumen de datos, umbrales, frecuencias).
- El modelo era una función de umbrales estáticos, no un modelo de ML entrenado.
- No había Feature Store ni separación entre pipeline de comunes y huérfanas.
- El monitoreo era conceptual: no había herramientas ni triggers definidos.
- No existía loop de re-entrenamiento automatizado.

---

*Equipo: RM · Tavo · Juanse — MIIA MLOps · ICESI · 2026*
