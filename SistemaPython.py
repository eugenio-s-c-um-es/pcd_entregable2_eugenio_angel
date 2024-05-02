# Singleton
class IoTDataManager:
    __instance = None

    def __init__(self):
        """ Constructor privado. """
        if IoTDataManager.__instance != None:
            raise Exception("Esta clase es un singleton!")
        else:
            IoTDataManager.__instance = self
            self.data = []  # Aquí almacenaremos los datos del sensor

    @staticmethod 
    def getInstance():
        """ Método de acceso estático. """
        if IoTDataManager.__instance == None:
            IoTDataManager()
        return IoTDataManager.__instance

    def add_data(self, data):
        """ Añade datos a la lista. """
        self.data.append(data)

    def get_data(self):
        """ Devuelve todos los datos. """
        return self.data

    # Aquí puedes añadir más métodos para procesar y visualizar los datos

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
    def update(self, data):
        pass


class IoTDataManager(Observable):
    __instance = None

    def __init__(self):
        super().__init__()
        if IoTDataManager.__instance != None:
            raise Exception("Esta clase es un singleton!")
        else:
            IoTDataManager.__instance = self
            self.data = []

    @staticmethod 
    def getInstance():
        if IoTDataManager.__instance == None:
            IoTDataManager()
        return IoTDataManager.__instance

    def add_data(self, data):
        self.data.append(data)
        self.notify(data)

    def get_data(self):
        return self.data

# Estrategia

from abc import ABC, abstractmethod
from statistics import mean, stdev

class Strategy(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class CalculateStats(Strategy):
    def execute(self, data):
        return mean(data), stdev(data)

class CheckThreshold(Strategy):
    def execute(self, data):
        threshold = 25  # Puedes cambiar este valor
        return max(data) > threshold

class CheckTemperatureIncrease(Strategy):
    def execute(self, data):
        return max(data) - min(data) > 10

class IoTDataManager(Observable):
    __instance = None

    def __init__(self):
        super().__init__()
        if IoTDataManager.__instance != None:
            raise Exception("Esta clase es un singleton!")
        else:
            IoTDataManager.__instance = self
            self.data = []
            self.strategy = None

    @staticmethod 
    def getInstance():
        if IoTDataManager.__instance == None:
            IoTDataManager()
        return IoTDataManager.__instance

    def add_data(self, data):
        self.data.append(data)
        self.notify(data)

    def get_data(self):
        return self.data

    def set_strategy(self, strategy):
        self.strategy = strategy

    def execute_strategy(self):
        if self.strategy is not None:
            return self.strategy.execute(self.data)

if __name__ == "__main__":
    pass