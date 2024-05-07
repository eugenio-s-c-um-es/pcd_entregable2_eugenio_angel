from abc import ABC, abstractmethod
from statistics import mean, stdev
from functools import reduce
from numpy import sqrt,random
import os
import time
import sys

# Observer
class Observable:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, data=None):
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
        self.notify(self.value)

class Sistema(Observer):
    __instance = None

    def __init__(self):
        self.data = []

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
        
    def establecerEstrategia(self, strategy):
        if not isinstance(strategy, Estrategia):
            raise TypeError("strategy debe ser una instancia de Estrategia")  
        self.strategy = strategy

    def ejecutarEstrategia(self, data = None):
        if self.strategy is not None:
            if data is None:
                return self.strategy.execute(self.data)
            return self.strategy.execute(data)
        
    def ComprobarUmbral(self,umbral = 33.2):
        res = True if list(filter(lambda x: x[1]>umbral,self.data[-12:])) else False

        if res:
            return "Se ha superado el umbral en los últimos 60 segundos"
        else:
            return "No se ha superado el umbral en los útlimos 60 segundos"

    ## Indica si se ha sobrepasado un DeltaT durante t: 2ºC 30s
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
        Q1 = sorted(data, key=lambda x: x[1])[n//4 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[n//4 -1][1] + sorted(data, key=lambda x: x[1])[n//4][1])/2
        mediana = sorted(data, key=lambda x: x[1])[n//2 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[n//2 -1][1] + sorted(data, key=lambda x: x[1])[n//2 ][1])/2
        Q3 = sorted(data, key=lambda x: x[1])[3*n//4 ][1] if n%2 != 0 else (sorted(data, key=lambda x: x[1])[3 *n//4 -1][1] + sorted(data, key=lambda x: x[1])[3 *n//4 ][1])/2 
        
        return f"Q1: {Q1} \nMediana: {mediana} \nQ3: {Q3}"       
        

if __name__ == "__main__":
    
    # Uso del patrón Singleton con atributos y métodos
    sistema = Sistema.obtenerInstancia()
    sensor = Sensor("Termómetro")
    sensor._observers.append(sistema)
    
    # Inicializar el sistema con 12 datos
    for i in range(12):
        sistema.actualizar((time.strftime(f"%Y-%m-%d %H:%M:%S"), round(random.normal(20,20),2)))
    
    import threading
    
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
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        sensor.set_value((time.strftime("%Y-%m-%d %H:%M:%S"), round(random.normal(20,20),2)))
        
        if choice == "1":
            print(sistema.obtenerDatos())
            print("\nEscribe otra opción si desea cambiar")
            
        elif choice == "2":
            sistema.establecerEstrategia(CalcularMediaDV())
            print(sistema.ejecutarEstrategia())
            sistema.establecerEstrategia(CalcularCuantiles())
            print(sistema.ejecutarEstrategia())
            sistema.establecerEstrategia(CalcularMaxMin())
            print(sistema.ejecutarEstrategia())
            print("\nEscribe otra opción si desea cambiar")
        
        elif choice == "3":
            print(sistema.ComprobarUmbral())
            print(sistema.ComprobarIncremento())
            print("\nEscribe otra opción si desea cambiar")
        
        elif choice == "4":
            sys.exit()
            
        else:
            print("Entrada incorrecta. Escribe uno de los números de las opciones")
            
        
        time.sleep(5)
        
        