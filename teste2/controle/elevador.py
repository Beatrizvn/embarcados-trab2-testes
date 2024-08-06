import threading
import time
from .config import ANDARES_BOTOES, ORDENS_BOTOES

class Elevador():
    def __init__(self, id) -> None:
        self.id = id
        self.__fila = []
        self.registradores = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.ordem_botao = ORDENS_BOTOES
        self.andar_botao = ANDARES_BOTOES
        
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
        if any(lista_andar[i] == 1 and 'S1' not in self.__fila for i in primeiro_indice):
            self.insereFila('S1')
        if any(lista_andar[i] == 1 and 'S2' not in self.__fila for i in segundo_indice):
            self.insereFila('S2')
        if any(lista_andar[i] == 1 and 'S3' not in self.__fila for i in terceiro_indice):
            self.insereFila('S3')
        if lista_andar[6] == 1:
            self.__fila = ['emergency']
