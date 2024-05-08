from abc import ABC, abstractmethod
from functools import reduce
from numpy import sqrt,random
import os
import time
import sys
import threading

# Observer
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

class Sensor(Observable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.notificar(self.value)

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
    
class HandlerEstrategia(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        sistema.establecerEstrategia(CalcularMediaDV())
        print(sistema.ejecutarEstrategia())
        sistema.establecerEstrategia(CalcularCuantiles())
        print(sistema.ejecutarEstrategia())
        sistema.establecerEstrategia(CalcularMaxMin())
        print(sistema.ejecutarEstrategia())
        #print("\nEscribe otra opción si desea cambiar")
        if self._next_handler:
            return self._next_handler.handle(sistema)
        

class HandlerUmbral(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        print(sistema.ComprobarUmbral())
        if self._next_handler:
            return self._next_handler.handle(sistema)

class HandlerIncremento(Handler):
    def handle(self, sistema):
        if not isinstance(sistema, Sistema):
            raise TypeError("sistema debe ser una instancia de Sistema")
        print(sistema.ComprobarIncremento())
        if self._next_handler:
            return self._next_handler.handle(sistema)
    
class Sistema(Observer):
    __instance = None
    
    
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

    def obtenerDatos(self):
        return self.data

    def actualizar(self,data):
        self.data.append(data)
        self.handler.handle(self)
        
    def establecerEstrategia(self, strategy):
        if not isinstance(strategy, Estrategia):
            raise TypeError("strategy debe ser una instancia de Estrategia")  
        self.strategy = strategy

    def ejecutarEstrategia(self, data = None):
        if self.strategy is not None:
            if data is None:
                return self.strategy.execute(self.data)
            return self.strategy.execute(data)
    
    """
    def manejar(self,peticion):
        if peticion == '1':
            print(self.obtenerDatos())
            print("\nEscribe otra opción si desea cambiar")
        elif peticion == '2':
            self.establecerEstrategia(CalcularMediaDV())
            print(self.ejecutarEstrategia())
            self.establecerEstrategia(CalcularCuantiles())
            print(self.ejecutarEstrategia())
            self.establecerEstrategia(CalcularMaxMin())
            print(self.ejecutarEstrategia())
            print("\nEscribe otra opción si desea cambiar")
        elif peticion == '3':
            print(self.ComprobarUmbral())
            print(self.ComprobarIncremento())
        elif peticion == '4':
            sys.exit()
        else:
            return super().handle(peticion)
    """
    
    def ComprobarUmbral(self,umbral = 33.2):
        res = True if list(filter(lambda x: x[1]>umbral,self.data[-12:])) else False

        if res:
            return "Se ha superado el umbral en los últimos 60 segundos"
        else:
            return "No se ha superado el umbral en los útlimos 60 segundos"

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

class CalcularMediaDV(Estrategia):
    def execute(self, data):
        n = len(data)
        media = round(reduce(lambda x,y : x + y[1], data, 0)/n,2)
        dev_tipica = round(sqrt((reduce(lambda x,y: x + (y[1]-media)**2, data, 0)-data[0][1] + (data[0][1]-media)**2)/n),2)
        
        return f"Media: {media} \nDesviación Típica: {dev_tipica}"
    
class CalcularMaxMin(Estrategia):
    def execute(self,data):
        maxi = reduce(lambda x,y: x if x>y[1] else y[1], data, -float("inf"))
        mini = reduce(lambda x,y: x if x<y[1] else y[1], data, float("inf"))
        
        return f"Máximo: {maxi} \nMínimo: {mini}"
    
class CalcularCuantiles(Estrategia):
    def execute(self,data):
        n = len(data)
        Q1 = round(sorted(data, key=lambda x: x[1])[n//4 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[n//4 -1][1] + sorted(data, key=lambda x: x[1])[n//4][1])/2,2)
        mediana = round(sorted(data, key=lambda x: x[1])[n//2 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[n//2 -1][1] + sorted(data, key=lambda x: x[1])[n//2 ][1])/2,2)
        Q3 = round(sorted(data, key=lambda x: x[1])[3*n//4 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[3 *n//4 -1][1] + sorted(data, key=lambda x: x[1])[3 *n//4 ][1])/2,2) 
        
        return f"Q1: {Q1} \nMediana: {mediana} \nQ3: {Q3}"       
        

if __name__ == "__main__":
    
    sistema = Sistema.obtenerInstancia()
    sensor = Sensor("Termómetro")
    sensor.alta(sistema)
    
    # Inicializar el sistema con 12 datos
    for i in range(12):
        sistema.actualizar((time.strftime(f"%Y-%m-%d %H:%M:%S"), round(random.normal(20,15),2)))
    
    """
    
    
    def get_user_input():
        global choice
        while True:
            choice = input("Loading...")
            os.system('cls' if os.name == 'nt' else 'clear')
            if choice == "4":
                break


    # Iniciar el thread de entrada del usuario
    
    print("Menu: Opción 1 por defecto, escriba la que quiera en consola")
    print("1. Comprobar datos actuales")
    print("2. Calcular Estadísticos")
    print("3. Umbral de temperatura y aumento de temperatura")
    print("4. Exit")
    
    user_input_thread = threading.Thread(target=get_user_input)

    choice = input("")
    
    user_input_thread.start()
    """
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        sensor.set_value((time.strftime("%Y-%m-%d %H:%M:%S"), round(random.normal(20,20),2)))
                      
        time.sleep(5)
        
        