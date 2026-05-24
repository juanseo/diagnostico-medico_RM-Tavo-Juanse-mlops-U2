# 🩺 Sistema de Diagnóstico Clínico — Solución Inicial (Unidad 1)

## Descripción del problema

En entornos clínicos, la evaluación rápida del estado de salud de un paciente es crítica para priorizar la atención médica. Este proyecto implementa un **sistema de predicción de estado de salud** que, dado un conjunto de parámetros fisiológicos básicos, clasifica automáticamente la condición del paciente en una de cuatro categorías diagnósticas:

| Estado | Descripción |
|---|---|
| `NO ENFERMO` | El paciente presenta parámetros dentro de rangos normales |
| `ENFERMEDAD LEVE` | Signos leves de alteración, puede requerir seguimiento |
| `ENFERMEDAD AGUDA` | Signos claros de enfermedad, requiere atención médica |
| `ENFERMEDAD CRÓNICA` | Signos severos y persistentes, requiere intervención urgente |

> ⚠️ **Este sistema es una simulación educativa.** La función de predicción utiliza umbrales estáticos con fines demostrativos y **no debe usarse para diagnósticos médicos reales.** En un entorno de producción, la función sería reemplazada por un modelo de ML entrenado y validado clínicamente.

---

## Propósito

Este repositorio corresponde a la **solución inicial presentada en la Semana 2 de la Unidad 1** del curso MLOps (MIIA — ICESI). Implementa un servicio de predicción médica contenerizado con Docker, expuesto mediante una interfaz web y una API REST.

**Equipo:** RM · Tavo · Juanse

---

## Parámetros de entrada

El médico debe ingresar **3 valores**:

| Parámetro | Tipo | Rango válido | Descripción |
|---|---|---|---|
| `temperatura` | `float` | 30.0 – 45.0 | Temperatura corporal en °C |
| `frecuencia_cardiaca` | `int` | 30 – 250 | Frecuencia cardíaca en bpm |
| `nivel_dolor` | `int` | 0 – 10 | Nivel de dolor (0 = sin dolor, 10 = máximo) |

---

## Lógica de predicción

La función `predecir_enfermedad()` asigna un puntaje parcial a cada parámetro y los suma para obtener un **score total (0–9)**:

| Parámetro | Condición | Puntos |
|---|---|---|
| Temperatura | < 37.2°C | 0 |
| Temperatura | 37.2–37.9°C | 1 |
| Temperatura | 38.0–39.4°C | 2 |
| Temperatura | ≥ 39.5°C | 3 |
| Frec. cardíaca | < 90 bpm | 0 |
| Frec. cardíaca | 90–109 bpm | 1 |
| Frec. cardíaca | 110–129 bpm | 2 |
| Frec. cardíaca | ≥ 130 bpm | 3 |
| Nivel dolor | 0–2 | 0 |
| Nivel dolor | 3–4 | 1 |
| Nivel dolor | 5–7 | 2 |
| Nivel dolor | 8–10 | 3 |

**Clasificación por score:**
- Score 0–1 → `NO ENFERMO`
- Score 2–3 → `ENFERMEDAD LEVE`
- Score 4–5 → `ENFERMEDAD AGUDA`
- Score 6–9 → `ENFERMEDAD CRÓNICA`

---

## Estructura del proyecto

```
diagnostico-medico/
├── Dockerfile          # Definición de la imagen Docker
├── requirements.txt    # Dependencias Python (Flask)
├── app.py              # Aplicación principal + función predecir_enfermedad()
├── templates/
│   └── index.html      # Interfaz web para el médico
└── README.md           # Este archivo
```

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) instalado en el sistema.
- No se requiere Python ni ninguna otra dependencia local.

---

## Construcción y ejecución con Docker

```bash
# Construir la imagen
docker build -t diagnostico-medico .

# Ejecutar el servicio (disponible en http://localhost:5000)
docker run -p 5000:5000 diagnostico-medico

# Modo detached (segundo plano)
docker run -d -p 5000:5000 --name diagnostico diagnostico-medico

# Detener el servicio
docker stop diagnostico
```

---

## Cómo obtener un diagnóstico

### Opción 1 — Página web

1. Abra su navegador: **http://localhost:5000**
2. Complete los tres campos del formulario.
3. Haga clic en **"Obtener diagnóstico"**.
4. El resultado aparece con código de color según la gravedad.

### Opción 2 — API REST

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

### Casos de prueba

| temperatura | frecuencia_cardiaca | nivel_dolor | Estado esperado |
|---|---|---|---|
| 36.6 | 72 | 1 | `NO ENFERMO` |
| 37.8 | 95 | 3 | `ENFERMEDAD LEVE` |
| 38.5 | 110 | 6 | `ENFERMEDAD AGUDA` |
| 40.2 | 145 | 9 | `ENFERMEDAD CRÓNICA` |

---

*Proyecto educativo — MIIA MLOps · ICESI · 2026*
