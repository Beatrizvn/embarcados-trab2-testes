import threading
import time

class Elevador:
    def __init__(self, id) -> None:
        self.id = id
        self.__fila = []
        self.registradores = b'\x00' * 11
        self.ordem_botao = ['BTS', 'B1D', 'B1S', 'B2D', 'B2S', 'B3D', 'BE', 'BT', 'B1', 'B2', 'B3']
        self.andar_botao = {
            'ST': ['BTS', 'BT'],
            'S1': ['B1D', 'B1S', 'B1'],
            'S2': ['B2D', 'B2S', 'B2'],
            'S3': ['B3D', 'B3']
        }
        self.indice_andar = {
            'ST': [0, 7],
            'S1': [1, 2, 8],
            'S2': [3, 4, 9],
            'S3': [5, 10]
        }
    
    def insereFila(self, andar):
        if andar not in self.__fila:
            print(f'Elevador {self.id} insere {andar}')
            self.__fila.append(andar)
        
    def removeFila(self):
        if self.__fila:
            andar_atual = self.__fila[0]
            self.__fila = [andar for andar in self.__fila if andar != andar_atual]
        
    def getFila(self):
        return self.__fila
    
    def setRegistrador(self, registradores):
        self.registradores = registradores
    
    def getAndarBotao(self):
        return self.andar_botao
    
    def trataRegistrador(self):
        lista_andar = list(self.registradores)
        
        for andar, indices in self.indice_andar.items():
            if any(lista_andar[i] == 1 and andar not in self.__fila for i in indices):
                self.insereFila(andar)
        
        if lista_andar[6] == 1:
            self.__fila = ['emergency']
