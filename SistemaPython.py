from abc import ABC, abstractmethod
from functools import reduce
from numpy import sqrt,random
import os
import time
import threading

# Definiomos la clase observer, así como las funciones básicas de alta, baja y notificar
class Observable:
    def __init__(self):
        self._observers = []

    def alta(self, observer):
        if not isinstance(observer, Observer):
            raise TypeError("observer debe ser una instancia o una subclase de Observer")
        if observer not in self._observers:
            self._observers.append(observer)

    def baja(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notificar(self, data=None):
        for observer in self._observers:
            observer.actualizar(data)


class Observer:
    @abstractmethod
    def actualizar(self, data):
        pass

# Definimos la clase sensor, que hereda de Observable, con su correspondiente función para 
# establecer el valor del sensor
class Sensor(Observable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.notificar(self.value)

# Creamos ahora la clase handler para establecer una cadena de responsabilidad que permita 
# gestionar los diferentes requisitos
class Handler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler):
        if not isinstance(handler, Handler):
            raise TypeError("handler debe ser una instancia de Handler")
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self):
        pass

# Handler para las estraegias
class HandlerEstrategia(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        sistema.establecerEstrategia(CalcularMediaDV())
        print(sistema.ejecutarEstrategia(sistema.data[-12:]))
        sistema.establecerEstrategia(CalcularCuantiles())
        print(sistema.ejecutarEstrategia(sistema.data[-12:]))
        sistema.establecerEstrategia(CalcularMaxMin())
        print(sistema.ejecutarEstrategia(sistema.data[-12:]))
        if self._next_handler:
            return self._next_handler.handle(sistema)
        
# Handler para comprobar el umbral
class HandlerUmbral(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        print(sistema.ComprobarUmbral())
        if self._next_handler:
            return self._next_handler.handle(sistema)

# Handler para comprobar el incremento
class HandlerIncremento(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        print(sistema.ComprobarIncremento())
        if self._next_handler:
            return self._next_handler.handle(sistema)
    
# Creamos la clase sistema, que hereda de Observer, y que será la encargada de gestionar los datos
class Sistema(Observer):
    __instance = None
    
    # Establecemos el orden de los handlers
    def __init__(self):
        super().__init__()
        self.data = []
        self.handler = HandlerEstrategia()
        self.handler.set_next(HandlerUmbral()).set_next(HandlerIncremento())

    @classmethod 
    def obtenerInstancia(cls):
        """ Método de acceso estático. """
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    # Función para obtener los datos
    def obtenerDatos(self):
        return self.data

    # Función para añadir datos sin notificar (para inicializar el sistema y tests)
    def add_data(self, data):
        self.data.append(data)
    
    # Función para actualizar los datos notificando a los observers
    def actualizar(self,data):
        self.data.append(data)
        self.handler.handle(self)
    
    # Función para establecer la estrategia 
    def establecerEstrategia(self, strategy):
        if not isinstance(strategy, Estrategia):
            raise TypeError("strategy debe ser una instancia de Estrategia")  
        self.strategy = strategy

    # Función para ejecutar la estrategia
    def ejecutarEstrategia(self, data = None):
        if self.strategy is not None:
            if data is None:
                return self.strategy.execute(self.data)
            return self.strategy.execute(data)
    
    # Función para comprobar si se ha superado un umbral
    def ComprobarUmbral(self,umbral = 33.2):
        res = True if list(filter(lambda x: x[1]>umbral,self.data)) else False

        if res:
            return "Se ha superado el umbral"
        else:
            return "No se ha superado el umbral"

    # Función para comprobar el incremento
    def ComprobarIncremento(self):
        self.establecerEstrategia(CalcularMaxMin())
        respuesta = self.ejecutarEstrategia(self.data[-6:])
        respuesta = respuesta.split(" ")
        max = respuesta[1]
        min = respuesta[3]
        
        if float(max) - float(min) >= 10:
            return "Ha habido un aumento de temperatura de más de 10ºC en los últimos 30s"
        return "No ha habido un aumento de temperatura de más de 10ºC en los últimos 30s"
    
# Estrategia
class Estrategia(ABC):
    @abstractmethod
    def execute(self, data):
        pass

# Estrategia concreta para Media y Desviación Típica
class CalcularMediaDV(Estrategia):
    def execute(self, data):
        n = len(data)
        media = reduce(lambda x,y : x + y[1], data, 0)/n
        dev_tipica = round(sqrt((reduce(lambda x,y: x + (y[1]-media)**2, data, 0))/(n-1)),2)
        
        return f"Media: {round(media,2)} \nDesviación Típica: {dev_tipica}"
    
# Estrategia concreta para Máximo y Mínimo
class CalcularMaxMin(Estrategia):
    def execute(self,data):
        maxi = reduce(lambda x,y: x if x>y[1] else y[1], data, -float("inf"))
        mini = reduce(lambda x,y: x if x<y[1] else y[1], data, float("inf"))
        
        return f"Máximo: {maxi} \nMínimo: {mini}"
    
# Estrategia concreta para Cuantiles
class CalcularCuantiles(Estrategia):
    def execute(self,data):
        n = len(data)
        sorted_data = sorted(data, key=lambda x: x[1])
        Q1 = round(sorted_data[n//4 ][1] if n%2 != 0 else (sorted_data[n//4 -1][1] + sorted_data[n//4][1])/2,2)
        mediana = round(sorted_data[n//2 ][1] if n%2 != 0 else (sorted_data[n//2 -1][1] + sorted_data[n//2 ][1])/2,2)
        Q3 = round(sorted_data[3*n//4 ][1] if n%2 != 0 else (sorted_data[3 *n//4 -1][1] + sorted_data[3 *n//4 ][1])/2,2) 
        
        return f"Q1: {Q1} \nMediana: {mediana} \nQ3: {Q3}"        

if __name__ == "__main__":
    
    # Creamos el sistema y el sensor
    sistema = Sistema.obtenerInstancia()
    sensor = Sensor("Termómetro")
    sensor.alta(sistema)
    
    # Inicializar el sistema con 12 datos
    for i in range(12):
        sistema.add_data((time.strftime(f"%Y-%m-%d %H:%M:%S"), round(random.normal(20,15),2)))
    
    # Función para obtener la entrada del usuario
    def get_user_input():
        global choice
        while True:
            choice = input("Loading...")
            os.system('cls' if os.name == 'nt' else 'clear')
            if choice == "2":
                break
    
    # Limpiar la pantalla
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Menú
    print("Menu:\n"
          "1. Mostrar datos actuales\n"
          "2. Exit\n"
          "Cualquier otra tecla para no mostrar datos actuales")

    # Pedimos la primera entrada del usuario mediante un input normal
    choice = input("")

    # Iniciar el thread de entrada del usuario    
    user_input_thread = threading.Thread(target=get_user_input)
    user_input_thread.start()
    
    # Bucle principal
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if choice == "1":
            print("\n", sistema.obtenerDatos())
            print("\nEscriba otra opción si desea cambiar\n")
        elif choice == "2":
            break
        sensor.set_value((time.strftime("%Y-%m-%d %H:%M:%S"), round(random.normal(20,15),2)))
                 
        time.sleep(5)
        
        