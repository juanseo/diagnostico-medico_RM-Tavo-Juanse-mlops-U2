# 🩺 Sistema de Diagnóstico Clínico — Servicio Docker

## Descripción

Este servicio simula un modelo de predicción de estado de salud para uso médico.
Dado un conjunto de parámetros clínicos del paciente, el sistema retorna uno de los
siguientes estados diagnósticos:

| Estado | Descripción |
|---|---|
| `NO ENFERMO` | El paciente presenta parámetros dentro de rangos normales |
| `ENFERMEDAD LEVE` | Signos leves de alteración, puede requerir seguimiento |
| `ENFERMEDAD AGUDA` | Signos claros de enfermedad, requiere atención médica |
| `ENFERMEDAD CRÓNICA` | Signos severos y persistentes, requiere intervención urgente |

El servicio se expone a través de una **página web** y un **endpoint de API REST**.

---

## Parámetros de entrada

El médico debe ingresar **3 valores**:

| Parámetro | Tipo | Rango válido | Descripción |
|---|---|---|---|
| `temperatura` | `float` | 30.0 – 45.0 | Temperatura corporal en °C |
| `frecuencia_cardiaca` | `int` | 30 – 250 | Frecuencia cardíaca en bpm |
| `nivel_dolor` | `int` | 0 – 10 | Nivel de dolor (0 = sin dolor, 10 = máximo) |

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) instalado en el sistema.
- No se requiere Python ni ninguna otra dependencia local.

---

## Construcción de la imagen

Desde la carpeta raíz del proyecto (donde se encuentra el `Dockerfile`):

```bash
docker build -t diagnostico-medico .
```

Esto descargará la imagen base de Python, instalará las dependencias y empaquetará
el servicio. El proceso tarda aproximadamente 1–2 minutos la primera vez.

---

## Ejecución del servicio

```bash
docker run -p 5000:5000 diagnostico-medico
```

El servicio quedará disponible en: **http://localhost:5000**

Para ejecutarlo en segundo plano (modo detached):

```bash
docker run -d -p 5000:5000 --name diagnostico diagnostico-medico
```

Para detenerlo:

```bash
docker stop diagnostico
```

---

## Cómo obtener un diagnóstico

### Opción 1 — Página web (recomendada para médicos)

1. Abra su navegador y vaya a: **http://localhost:5000**
2. Complete los tres campos del formulario.
3. Haga clic en **"Obtener diagnóstico"**.
4. El resultado aparece en pantalla con un código de color según la gravedad.

### Opción 2 — API REST (para integración con sistemas externos)

**Endpoint:** `POST /predecir`  
**Content-Type:** `application/json`

#### Ejemplo con `curl`

```bash
curl -X POST http://localhost:5000/predecir \
     -H "Content-Type: application/json" \
     -d '{"temperatura": 38.5, "frecuencia_cardiaca": 110, "nivel_dolor": 6}'
```

#### Respuesta exitosa

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

#### Ejemplos de casos de prueba

| temperatura | frecuencia_cardiaca | nivel_dolor | Estado esperado |
|---|---|---|---|
| 36.6 | 72 | 1 | `NO ENFERMO` |
| 37.8 | 95 | 3 | `ENFERMEDAD LEVE` |
| 38.5 | 110 | 6 | `ENFERMEDAD AGUDA` |
| 40.2 | 145 | 9 | `ENFERMEDAD CRÓNICA` |

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

## Notas importantes

> ⚠️ **Este sistema es una simulación educativa.** La función de predicción utiliza
> umbrales estáticos con fines demostrativos y **no debe usarse para diagnósticos
> médicos reales.** En un entorno de producción, la función sería reemplazada por
> un modelo de ML entrenado y validado clínicamente.
