import pytest
import time
from SistemaPython import Sistema, Sensor, CalcularMediaDV, CalcularMaxMin, CalcularCuantiles

@pytest.fixture
def sistema_fixture():
    sistema = Sistema.obtenerInstancia()
    sensor = Sensor("Termómetro")
    sensor._observers.append(sistema)
    return sistema

def test_actualizar(sistema_fixture):
    loongitud = len(sistema_fixture.obtenerDatos())
    sistema_fixture.actualizar((time.strftime("%Y-%m-%d %H:%M:%S"), 30.0))
    assert len(sistema_fixture.obtenerDatos()) == loongitud + 1

def test_establecerEstrategia(sistema_fixture):
    estrategia = CalcularMediaDV()
    sistema_fixture.establecerEstrategia(estrategia)
    assert sistema_fixture.strategy == estrategia

def test_ejecutarEstrategia(sistema_fixture):
    estrategia = CalcularMaxMin()
    sistema_fixture.establecerEstrategia(estrategia)
    resultado = sistema_fixture.ejecutarEstrategia([(time.strftime("%Y-%m-%d %H:%M:%S"), 25.0), (time.strftime("%Y-%m-%d %H:%M:%S"), 30.0)])
    assert resultado == "Máximo: 30.0 \nMínimo: 25.0"

def test_ComprobarUmbral(sistema_fixture):
    sistema_fixture.add_data((time.strftime("%Y-%m-%d %H:%M:%S"), 20.0))
    sistema_fixture.add_data((time.strftime("%Y-%m-%d %H:%M:%S"), 25.0))
    sistema_fixture.add_data((time.strftime("%Y-%m-%d %H:%M:%S"), 30.0))
    resultado = sistema_fixture.ComprobarUmbral(27.5)
    assert resultado == "Se ha superado el umbral en los últimos 60 segundos"

def test_ComprobarIncremento(sistema_fixture):
    sistema_fixture.establecerEstrategia(CalcularMaxMin())
    resultado = sistema_fixture.ComprobarIncremento()
    assert resultado == "Ha habido un aumento de temperatura de más de 10ºC en los últimos 30s"
    
if __name__ == '__main__':
    pytest.main()
