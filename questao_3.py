import logger
from threading import Thread, Semaphore 
import random
from time import sleep

log = logger.get_logger("Bar do Auri")


def sentar(aluno):
    log.info(f"Aluno {aluno} sentou-se...")


def bebe(aluno):
    log.info(f"Aluno {aluno} está bebendo...")


def sai(aluno):
    log.info(f"Aluno {aluno} saiu...")


class Counter():
    def __init__(self, alunos):
        """
        Contador para ser reusado como referencia para
        a classe Aluno.
        Contador usa a logica do problema 7.6.1 do livro
        The Little Book of Semaphores
        """
        self.alunos = alunos
        self.eating = 0
        self.ready_to_leave = 0
        self.mutex = Semaphore(1)
        self.ok_to_leave = Semaphore(0)


class Aluno(Thread):

    def __init__(self, id, counter):
        Thread.__init__(self)
        self.id = id
        self.counter = counter
        self.start()

    def run(self):
        sentar(self.id)
        self.counter.mutex.acquire()
        self.counter.eating += 1
        if self.counter.eating == 2 and self.counter.ready_to_leave == 1:
            self.counter.ok_to_leave.release()
            self.counter.ready_to_leave -= 1

        self.counter.mutex.release()

        bebe(self.id)

        self.counter.mutex.acquire()
        self.counter.eating -= 1
        self.counter.ready_to_leave += 1

        if self.counter.eating == 1 and self.counter.ready_to_leave == 1:
            self.counter.mutex.release()
            self.counter.ok_to_leave.acquire()
        elif self.counter.eating == 0 and self.counter.ready_to_leave == 2:
            self.counter.ok_to_leave.release()
            self.counter.ready_to_leave -= 2
            self.counter.mutex.release()
        else :
            self.counter.ready_to_leave -= 1
            self.counter.mutex.release()

        sai(self.id)


if __name__ == "__main__":
    alunos = int(input("Digite a quantidade de alunos no bar: "))
    counter = Counter(alunos)
    for num in range(alunos):
        _aluno = Aluno(num, counter)
