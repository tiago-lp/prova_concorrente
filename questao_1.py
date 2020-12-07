import logger
from threading import Semaphore, Thread
from time import sleep
import random


log = logger.get_logger("Carona Uber")


def carregar():
    log.info("Carro está pronto pra carregar...")


def descarregar():
    log.info("O carro está descarregando...")


def correr():
    log.info("O carro está correndo!")


def embarcar(id):
    log.info(f"O passageiro {id} está embarcando...")


def parar():
    log.info("O carro parou.")


def desembarcar(id):
    log.info(f"O passageiro {id} está desembarcando...")


def finalizar():
    log.info("Nenhum passageiro esperando. Finalizando o dia de Uber.")
    exit()


def falta_passageiros(num, capacidade):
    log.info(f"Não é possível correr. Tem apenas {num} querendo embarcar. O carro precisa ter {capacidade} passageiros para correr.")
    exit()


class Counter():
    def __init__(self, capacidade_max_carro, num_passageiros):
        """
        Classe com atributos baseado na solucao dada no capitulo 5.8
        do livro The Little Book of Semaphores. A classe é usada como
        argumento de construção das classes Carro e Passageiro.
        """
        self.capacidade_max_carro = capacidade_max_carro
        self.num_passageiros = num_passageiros
        self.ja_viajaram = 0
        self.boarders = 0
        self.unboarders = 0
        self.mutex = Semaphore(1)
        self.mutex2 = Semaphore(1)
        self.boardQueue = Semaphore(0)
        self.unboard_queue = Semaphore(0)
        self.all_aboard = Semaphore(0)
        self.all_ashore = Semaphore(0)


class Carro(Thread):
    def __init__(self, counter):
        """
        Classe carro inicializa herdando da classe Thread
        e a inicializa.

        Params
        ------
        counter : Counter
            Referencia para a contagem de passageiros, capacidade
            do carro e semaforos utilizados.
        """
        Thread.__init__(self)
        self.counter = counter
        self.start()

    def sobrou_pessoas(self):
        """Verifica se sobrou pessoas esperando para embarcar
        que nao contempla a lotacao do carro.
        """
        return self.counter.ja_viajaram + self.counter.capacidade_max_carro > self.counter.num_passageiros

    def nao_tem_passageiros(self):
        """Verifica se nao tem mais nenhum passageiro esperando para embarcar."""
        return self.counter.ja_viajaram == self.counter.num_passageiros

    def sinaliza_passageiros(self, sem):
        """Isto eh necessario em python
        notei que o release do semaforo nativo nao aceita argumentos.
        Eu poderia criar o meu proprio semaforo,
        mas para reusar a implementacao nativa percorri a quantidade
        de vezes que eh preciso sinalizar, que seria o C definido no problema
        (capacidade do carro)

        params
        -------
        sem : Semaphore
            Referencia do semaforo que desejo sinalizar
        """
        for i in range(self.counter.capacidade_max_carro):
            sem.release()
            sleep(random.randrange(0,2))

    def run(self):
        while True:
            carregar()

            if self.nao_tem_passageiros():
                finalizar()

            if self.sobrou_pessoas():
                sobraram = self.counter.num_passageiros - self.counter.ja_viajaram
                falta_passageiros(sobraram, self.counter.capacidade_max_carro)


            self.sinaliza_passageiros(self.counter.boardQueue)
                
            self.counter.all_aboard.acquire()
            correr()
            sleep(random.randrange(0,2))
            parar()
            sleep(random.randrange(0,2))
            if self.counter.boarders == 0:
                descarregar()
                self.sinaliza_passageiros(self.counter.unboard_queue)
                self.counter.all_ashore.acquire()


class Passageiro(Thread):

    def __init__(self, counter, id):
        """
        Classe passageiro inicializa herdando da classe Thread
        e a inicializa.

        Params
        ------
        counter : Counter
            Referencia para a contagem de passageiros, capacidade
            do carro e semaforos utilizados.
        id : str, int
            Identificador do passageiro para mostrar nos logs
        """
        Thread.__init__(self)
        self.id = id
        self.counter = counter
        self.start()

    def run(self):
        self.counter.boardQueue.acquire()
        embarcar(self.id)
        self.counter.mutex.acquire()
        self.counter.boarders += 1
        if self.counter.boarders == self.counter.capacidade_max_carro:
            self.counter.all_aboard.release()
            self.counter.boarders = 0

        self.counter.mutex.release()
        self.counter.unboard_queue.acquire()
        desembarcar(self.id)
        self.counter.mutex2.acquire()
        self.counter.unboarders += 1
        self.counter.ja_viajaram += 1
        if self.counter.unboarders == self.counter.capacidade_max_carro:
            self.counter.all_ashore.release()
            self.counter.unboarders = 0

        self.counter.mutex2.release()


if __name__ == "__main__":
    capacidade_carro = int(input("Digite a capacidade do carro: "))
    numero_passageiros = int(input("Digite a quantidade de passageiros: "))
    counter = Counter(capacidade_carro, numero_passageiros)
    _carro = Carro(counter)
    for num in range(numero_passageiros):
        _passageiro = Passageiro(counter, num)
