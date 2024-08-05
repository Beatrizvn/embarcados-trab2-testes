import threading
import time

class Elevador():
    def __init__(self, id) -> None:
        self.id = id
        self.__fila = []
        self.registradores = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        # self.ordem_botao = ['BTS', 'B1D', 'B1S', 'B2D', 'B2S', 'B3D', 'BEmergencia', 'BT', 'B1', 'B2', 'B3']
        self.ordem_botao = ['BTS', 'B1D', 'B1S', 'B2D', 'B2S', 'B3D', 'BE', 'BT', 'B1', 'B2', 'B3']
        self.andar_botao = {'ST': ['BTS', 'BT'], 'S1': ['B1D', 'B1S', 'B1'], 'S2': ['B2D', 'B2S', 'B2'], 'S3': ['B3D', 'B3']}
        
    def insereFila(self, andar):
        print(f'Elevador {self.id} insere {andar}')
        self.__fila.append(andar)
        
    def removeFila(self):
        andar_atual = self.__fila[0]
        while andar_atual in self.__fila:
            self.__fila.remove(andar_atual)
        
    def getFila(self):
        return self.__fila
    
    def setRegistrador(self, registradores):
        self.registradores = registradores
    
    def getAndarBotao(self):
        return self.andar_botao
    
    def trataRegistrador(self):
        lista_andar = list(self.registradores)
        
        terreo_indice = [0, 7]
        primeiro_indice = [1, 2, 8]
        segundo_indice = [3, 4, 9]
        terceiro_indice = [5, 10]
        
        if any(lista_andar[i] == 1 and 'ST' not in self.__fila for i in terreo_indice):
            self.insereFila('ST')
        elif any(lista_andar[i] == 1 and 'S1' not in self.__fila for i in primeiro_indice):
            self.insereFila('S1')
        elif any(lista_andar[i] == 1 and 'S2' not in self.__fila for i in segundo_indice):
            self.insereFila('S2')
        elif any(lista_andar[i] == 1 and 'S3' not in self.__fila for i in terceiro_indice):
            self.insereFila('S3')
        elif lista_andar[6] == 1:
            self.__fila = ['emergency']
        # self.registradores = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'