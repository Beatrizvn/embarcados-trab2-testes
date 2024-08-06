import threading
import time
from .config import ORDENS_BOTOES, ANDARES_BOTOES

class Elevador:
    def __init__(self, id):
        self.id = id
        self.__fila = []
        self.registradores = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        self.ordem_botao = ORDENS_BOTOES
        self.andar_botao = ANDARES_BOTOES
        
    def insere_fila(self, andar):
        print(f'Elevador {self.id} insere {andar}')
        self.__fila.append(andar)
        
    def remove_fila(self):
        andar_atual = self.__fila[0]
        while andar_atual in self.__fila:
            self.__fila.remove(andar_atual)
        
    def get_fila(self):
        return self.__fila
    
    def set_registrador(self, registradores):
        self.registradores = registradores
    
    def get_andar_botao(self):
        return self.andar_botao
    
def trata_registrador(self):
    lista_andar = list(self.registradores)
    
    indices_por_andar = {
        'ST': [0, 7],
        'S1': [1, 2, 8],
        'S2': [3, 4, 9],
        'S3': [5, 10],
    }

    # Checa emergências
    if lista_andar[6] == 1:
        self.__fila = ['emergency']
        return

    # Adiciona andares à fila
    for andar, indices in indices_por_andar.items():
        if any(lista_andar[i] == 1 for i in indices) and andar not in self.__fila:
            self.insere_fila(andar)

