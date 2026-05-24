from flask import Flask, request, jsonify, render_template
import datetime
import json

app = Flask(__name__)

# Almacenamiento en memoria para las estadísticas
estadisticas_globales = {
    "conteo_por_categoria": {
        "NO ENFERMO": 0,
        "ENFERMEDAD LEVE": 0,
        "ENFERMEDAD AGUDA": 0,
        "ENFERMEDAD CRÓNICA": 0,
        "ENFERMEDAD TERMINAL": 0
    },
    "ultimas_predicciones": [],
    "fecha_ultima_prediccion": None
}


def predecir_enfermedad(temperatura: float, frecuencia_cardiaca: int, nivel_dolor: int) -> str:
    """
    Función simulada que predice el estado de salud de un paciente
    basada en tres síntomas: temperatura corporal, frecuencia cardiaca
    y nivel de dolor (escala 0-10).

    Retorna uno de los cinco estados:
        - NO ENFERMO
        - ENFERMEDAD LEVE
        - ENFERMEDAD AGUDA
        - ENFERMEDAD CRÓNICA
        - ENFERMEDAD TERMINAL
    """
    if not (0 <= nivel_dolor <= 10):
        raise ValueError("El nivel de dolor debe estar entre 0 y 10.")
    if not (30 <= temperatura <= 45):
        raise ValueError("La temperatura debe estar entre 30°C y 45°C.")
    if not (30 <= frecuencia_cardiaca <= 250):
        raise ValueError("La frecuencia cardíaca debe estar entre 30 y 250 bpm.")

    score = 0

    # Temperatura
    if temperatura < 37.2:
        score += 0
    elif temperatura < 38.0:
        score += 1
    elif temperatura < 39.5:
        score += 2
    else:
        score += 3

    # Frecuencia cardiaca
    if frecuencia_cardiaca < 90:
        score += 0
    elif frecuencia_cardiaca < 110:
        score += 1
    elif frecuencia_cardiaca < 130:
        score += 2
    else:
        score += 3

    # Nivel de dolor
    if nivel_dolor <= 2:
        score += 0
    elif nivel_dolor <= 4:
        score += 1
    elif nivel_dolor <= 7:
        score += 2
    else:
        score += 3

    # Clasificación basada en score total (0-9)
    if score <= 1:
        return "NO ENFERMO"
    elif score <= 3:
        return "ENFERMEDAD LEVE"
    elif score <= 5:
        return "ENFERMEDAD AGUDA"
    elif score <= 7:
        return "ENFERMEDAD CRÓNICA"
    else:
        return "ENFERMEDAD TERMINAL"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predecir", methods=["POST"])
def predecir():
    """Endpoint que acepta JSON o form-data y devuelve el diagnóstico."""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        temperatura = float(data["temperatura"])
        frecuencia_cardiaca = int(data["frecuencia_cardiaca"])
        nivel_dolor = int(data["nivel_dolor"])

        resultado = predecir_enfermedad(temperatura, frecuencia_cardiaca, nivel_dolor)

        parametros = {
            "temperatura": temperatura,
            "frecuencia_cardiaca": frecuencia_cardiaca,
            "nivel_dolor": nivel_dolor,
        }

        # Actualizar estadísticas y guardar en archivo log
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if resultado in estadisticas_globales["conteo_por_categoria"]:
            estadisticas_globales["conteo_por_categoria"][resultado] += 1
        else:
            estadisticas_globales["conteo_por_categoria"][resultado] = 1

        registro = {
            "fecha": ahora,
            "resultado": resultado,
            "parametros": parametros
        }
        
        estadisticas_globales["ultimas_predicciones"].insert(0, registro)
        estadisticas_globales["ultimas_predicciones"] = estadisticas_globales["ultimas_predicciones"][:5]
        estadisticas_globales["fecha_ultima_prediccion"] = ahora

        with open("predicciones.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(registro) + "\n")

        return jsonify({
            "estado": resultado,
            "parametros": parametros,
        })

    except KeyError as e:
        return jsonify({"error": f"Parámetro faltante: {e}"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/estadisticas", methods=["GET"])
def obtener_estadisticas():
    """Endpoint para obtener las estadísticas de predicciones."""
    return jsonify(estadisticas_globales)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
