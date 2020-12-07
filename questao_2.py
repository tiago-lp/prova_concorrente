import logger
from threading import Thread, Semaphore 
import random
from time import sleep


log = logger.get_logger("Atravessando Bodocongó")


def embarcar(aluno):
    log.info(f"{aluno} está embarcando...")


def remar(aluno):
    log.info(f"{aluno} está REMANDO...")


class Barrier():
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Semaphore(1)
        self.barrier = Semaphore(0)

    def wait(self):
        self.mutex.acquire()
        self.count = self.count + 1
        self.mutex.release()
        if self.count == self.n:
            self.barrier.release()
        self.barrier.acquire()
        self.barrier.release()


class Counter():
    def __init__(self, ufcg, uepb):
        """Contador para ser reusado como referencia para
        as classes AlunoUFCG e AlunoUEPB.
        Contador usa a logica do problema 5.7 do livro
        The Little Book of Semaphores
        """
        self.num_ufcg = ufcg
        self.num_uepb = uepb
        self.barrier = Barrier(4)
        self.mutex = Semaphore(1)
        self.alunos_ufcg = 0
        self.alunos_uepb = 0
        self.ufcg_queue = Semaphore(0)
        self.uepb_queue = Semaphore(0)


class AlunoUFCG(Thread):

    def __init__(self, id, counter):
        Thread.__init__(self)
        self.id = id
        self.counter = counter
        self.name = "Aluno da UFCG"
        self.captain = False
        self.start()

    def release_all(self):
        for i in range(4):
            self.counter.ufcg_queue.release()

    def run(self):

        sleep(random.randrange(0,2))

        self.counter.mutex.acquire()
        self.counter.alunos_ufcg += 1
        if self.counter.alunos_ufcg == 4:
            self.release_all()
            self.counter.alunos_ufcg = 0
            self.captain = True
        elif self.counter.alunos_ufcg == 2 and self.counter.alunos_uepb >= 2:
            self.counter.ufcg_queue.release()
            self.counter.ufcg_queue.release()
            self.counter.uepb_queue.release()
            self.counter.uepb_queue.release()
            self.counter.alunos_ufcg -= 2
            self.counter.alunos_uepb -= 2
            self.captain = True
        else:
            self.counter.mutex.release()
        
        self.counter.ufcg_queue.acquire()
        embarcar(f"{self.name} - matricula: {self.id}")
        self.counter.barrier.wait()
        if self.captain:
            remar(f"{self.name} - matricula: {self.id}")
            self.counter.mutex.release()


class AlunoUEPB(Thread):

    def __init__(self, id, counter):
        Thread.__init__(self)
        self.id = id
        self.counter = counter
        self.name = "Aluno da UEPB"
        self.captain = False
        self.start()

    def release_all(self):
        for i in range(4):
            self.counter.uepb_queue.release()

    def run(self):

        sleep(random.randrange(0,2))

        self.counter.mutex.acquire()
        self.counter.alunos_uepb += 1
        if self.counter.alunos_uepb == 4:
            self.release_all()
            self.counter.alunos_uepb = 0
            self.captain = True
        elif self.counter.alunos_uepb == 2 and self.counter.alunos_ufcg >= 2:
            self.counter.uepb_queue.release()
            self.counter.uepb_queue.release()
            self.counter.ufcg_queue.release()
            self.counter.ufcg_queue.release()
            self.counter.alunos_uepb -= 2
            self.counter.alunos_ufcg -= 2
            self.captain = True
        else:
            self.counter.mutex.release()
        
        self.counter.uepb_queue.acquire()
        embarcar(f"{self.name} - matricula: {self.id}")
        self.counter.barrier.wait()
        if self.captain:
            remar(f"{self.name} - matricula: {self.id}")
            self.counter.mutex.release()


if __name__ == "__main__":
    alunos_ufcg = int(input("Digite a quantidade de alunos da UFCG: "))
    alunos_uepb = int(input("Digite a quantidade de alunos da UEPB: "))
    counter = Counter(alunos_ufcg, alunos_uepb)
    for num in range(alunos_ufcg):
        matricula = f"uf_{num}"
        _aluno = AlunoUFCG(matricula, counter)

    for num in range(alunos_uepb):
        matricula = f"ue_{num}"
        _aluno = AlunoUEPB(matricula, counter)
