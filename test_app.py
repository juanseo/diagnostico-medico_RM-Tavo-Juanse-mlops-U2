import pytest
import json
from app import app, estadisticas_globales

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_enfermedad_terminal(client):
    """Prueba 1: Verificar que un caso extremo arroje 'ENFERMEDAD TERMINAL'."""
    response = client.post('/predecir', json={
        "temperatura": 41.0,
        "frecuencia_cardiaca": 180,
        "nivel_dolor": 10
    })
    data = json.loads(response.data)
    assert response.status_code == 200
    assert data["estado"] == "ENFERMEDAD TERMINAL"

def test_estadisticas_iniciales(client):
    """Prueba 2: Verificar que las estadísticas existen y tienen conteos validos iniciales."""
    # Como puede ejecutarse despues de otros tests, al menos verificamos que la estructura es correcta.
    response = client.get('/estadisticas')
    data = json.loads(response.data)
    assert response.status_code == 200
    assert "conteo_por_categoria" in data
    assert "NO ENFERMO" in data["conteo_por_categoria"]
    assert "ENFERMEDAD TERMINAL" in data["conteo_por_categoria"]

def test_actualizacion_estadisticas(client):
    """Prueba 3: Verificar que las estadísticas se actualizan tras una predicción."""
    # Obtenemos el conteo antes
    res_antes = client.get('/estadisticas')
    conteo_antes = json.loads(res_antes.data)["conteo_por_categoria"]["NO ENFERMO"]

    # Hacemos una predicción que resulta en NO ENFERMO (ej: parametros normales)
    client.post('/predecir', json={
        "temperatura": 36.8,
        "frecuencia_cardiaca": 75,
        "nivel_dolor": 1
    })

    # Obtenemos el conteo despues
    res_despues = client.get('/estadisticas')
    data_despues = json.loads(res_despues.data)
    conteo_despues = data_despues["conteo_por_categoria"]["NO ENFERMO"]

    assert conteo_despues == conteo_antes + 1
    assert len(data_despues["ultimas_predicciones"]) > 0
    assert data_despues["ultimas_predicciones"][0]["resultado"] == "NO ENFERMO"

def test_endpoint_estadisticas_json(client):
    """Prueba 4: Verificar que el endpoint responde en formato JSON."""
    response = client.get('/estadisticas')
    assert response.status_code == 200
    assert response.is_json
