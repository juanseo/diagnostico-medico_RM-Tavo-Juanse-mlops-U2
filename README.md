# 🩺 Sistema de Diagnóstico Clínico — MLOps Unidad 2

## Descripción del problema

En entornos clínicos, la evaluación rápida del estado de salud de un paciente es crítica para priorizar la atención médica. Este proyecto implementa un **sistema de predicción de estado de salud** que, dado un conjunto de parámetros fisiológicos básicos, clasifica automáticamente la condición del paciente en una de cinco categorías diagnósticas:

| Estado | Descripción |
|---|---|
| `NO ENFERMO` | Parámetros dentro de rangos normales |
| `ENFERMEDAD LEVE` | Signos leves de alteración; puede requerir seguimiento |
| `ENFERMEDAD AGUDA` | Signos claros de enfermedad; requiere atención médica |
| `ENFERMEDAD CRÓNICA` | Signos severos y persistentes; requiere intervención urgente |
| `ENFERMEDAD TERMINAL` | Estado crítico extremo; requiere atención inmediata de emergencia |

> ⚠️ **Sistema educativo y de simulación.** La función de predicción utiliza umbrales estáticos con fines demostrativos y **no debe usarse para diagnósticos médicos reales.** En producción, sería reemplazada por un modelo de ML entrenado y validado clínicamente.

---

## Propósito del repositorio

Este repositorio es el entregable del proyecto de la **Unidad 2 del curso de MLOps** (Maestría en Inteligencia Artificial Aplicada — ICESI). El objetivo es demostrar buenas prácticas de MLOps aplicadas a un sistema de predicción médica:

- Control de versiones y flujo de trabajo con Git (ramas, PRs, merges)
- Contenerización del servicio con Docker
- Integración continua y despliegue continuo (CI/CD) con GitHub Actions
- Publicación de imágenes en GitHub Packages

**Equipo:** RM · Tavo · Juanse

---

## Parámetros de entrada

El sistema recibe **3 parámetros fisiológicos**:

| Parámetro | Tipo | Rango válido | Descripción |
|---|---|---|---|
| `temperatura` | `float` | 30.0 – 45.0 | Temperatura corporal en °C |
| `frecuencia_cardiaca` | `int` | 30 – 250 | Frecuencia cardíaca en bpm |
| `nivel_dolor` | `int` | 0 – 10 | Nivel de dolor (0 = sin dolor, 10 = máximo) |

---

## Estructura del repositorio

```
diagnostico-medico_RM-Tavo-Juanse-mlops-U2/
├── Dockerfile              # Definición de la imagen Docker (python:3.11-slim)
├── requirements.txt        # Dependencias Python (Flask)
├── app.py                  # Aplicación Flask: lógica de predicción + endpoints REST
├── templates/
│   └── index.html          # Interfaz web para el médico (formulario + resultados)
└── README.md               # Este archivo
```

### Descripción de archivos principales

- **`app.py`**: Contiene la función `predecir_enfermedad()` (sistema de puntuación por umbrales) y los endpoints Flask:
  - `GET /` — Interfaz web
  - `POST /predecir` — API REST para obtener diagnóstico
  - `GET /estadisticas` — Estadísticas de predicciones realizadas
- **`Dockerfile`**: Empaqueta la aplicación en una imagen Docker lista para producción
- **`templates/index.html`**: UI web con código de colores según gravedad del diagnóstico

---

## Ejecución rápida con Docker

```bash
# Construir la imagen
docker build -t diagnostico-medico .

# Ejecutar el servicio
docker run -p 5000:5000 diagnostico-medico
```

El servicio estará disponible en: **http://localhost:5000**

---

## API REST

**Endpoint:** `POST /predecir`  
**Content-Type:** `application/json`

```bash
curl -X POST http://localhost:5000/predecir \
     -H "Content-Type: application/json" \
     -d '{"temperatura": 38.5, "frecuencia_cardiaca": 110, "nivel_dolor": 6}'
```

**Respuesta:**
```json
{
  "estado": "ENFERMEDAD AGUDA",
  "parametros": {
    "temperatura": 38.5,
    "frecuencia_cardiaca": 110,
    "nivel_dolor": 6
  }
}
```

### Casos de prueba de referencia

| temperatura | frecuencia_cardiaca | nivel_dolor | Estado esperado |
|---|---|---|---|
| 36.6 | 72 | 1 | `NO ENFERMO` |
| 37.8 | 95 | 3 | `ENFERMEDAD LEVE` |
| 38.5 | 110 | 6 | `ENFERMEDAD AGUDA` |
| 40.2 | 145 | 9 | `ENFERMEDAD CRÓNICA` |
| 41.5 | 180 | 10 | `ENFERMEDAD TERMINAL` |

---

## Flujo de ramas (MLOps U2)

```
main
├── solucion-inicial          → Solución base de la Unidad 1
├── añadir-enfermedad-terminal → Requisito 1: 5ª categoría diagnóstica
└── añadir-estadisticas-predicciones → Requisito 2: sistema de estadísticas
```

---

*Proyecto educativo — MIIA MLOps · ICESI · 2026*
