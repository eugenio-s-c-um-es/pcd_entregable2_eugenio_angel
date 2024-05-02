from abc import ABC, abstractmethod
from statistics import mean, stdev
from functools import reduce
from numpy import sqrt

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
            observer.update(data)


class Observer:
    @abstractmethod
    def update(self, data):
        pass

class Sensor(Observable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.notify_observers(self.value)

class Sistema(Observer):
    __instance = None

    def __init__(self):
        self.data = []

    @classmethod 
    def getInstance(cls):
        """ Método de acceso estático. """
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance

    def add_data(self, data):
        self.data.append(data)
        self.notify(data)

    def get_data(self):
        return self.data

    def update(self,data):
        pass
        
    def set_strategy(self, strategy):
        self.strategy = strategy

    def execute_strategy(self):
        if self.strategy is not None:
            return self.strategy.execute(self.data)
# Estrategia

class Strategy(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class CalcularMediaDV(Strategy):
    def execute(self, data):
        n = len(data)
        media = reduce(lambda x,y : x + y, data)/n
        dev_tipica = sqrt((reduce(lambda x,y: x + (y-media)**2, data)-data[0] + (data[0]-media)**2)/n)
        
        return f"Media: {media} \nDesviación Típica: {dev_tipica}"
    
class CalcularMaxMin(Strategy):
    def execute(self,data):
        maxi = reduce(lambda x,y: x if x>y else y, data)
        mini = reduce(lambda x,y: x if x<y else y, data)
        
        return f"Máximo: {maxi} \nMínimo: {mini}"
    
class CalcularCuantiles(Strategy):
    def execute(self,data):
        n = len(data)
        Q1 = sorted(data)[n//4 ] if n%2 != 0 else (sorted(data)[n//4 -1] + sorted(data)[n//4])/2
        mediana = sorted(data)[n//2 ] if n%2 != 0 else (sorted(data)[n//2 -1] + sorted(data)[n//2 ])/2
        Q3 = sorted(data)[3*n//4 ] if n%2 != 0 else (sorted(data)[3 *n//4 -1] + sorted(data)[3 *n//4 ])/2 
        
        return f"Q1: {Q1} \nMediana: {mediana} \nQ3: {Q3}"       
        
class CheckThreshold(Strategy):
    def execute(self, data):
        threshold = 25  # Puedes cambiar este valor
        return max(data) > threshold

class CheckTemperatureIncrease(Strategy):
    def execute(self, data):
        return max(data) - min(data) > 10

if __name__ == "__main__":
    # Uso del patrón Singleton con atributos y métodos
    sistema = Sistema.getInstance()
