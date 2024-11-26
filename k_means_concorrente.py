import numpy as np
from multiprocessing import shared_memory

# Função executada pelos processos
def Calculadores(process_id, shared_mem_centroides, shared_mem_data, shape_centroides, shape_data, dtype_centroides,
                 dtype_data, start_row, end_row, num_processos, num_centroides, lock, lock_soma, counter, sem_m, sem_c, stop_condition):
    # Acessa a memória compartilhada dos centroides
    existing_shm1 = shared_memory.SharedMemory(name=shared_mem_centroides)
    centroides = np.ndarray(shape_centroides, dtype=dtype_centroides, buffer=existing_shm1.buf)

    # Acessa a memória compartilhada dos dados
    existing_shm2 = shared_memory.SharedMemory(name=shared_mem_data)
    data = np.ndarray(shape_data, dtype=dtype_data, buffer=existing_shm2.buf)

    # Subconjunto dos dados da memória compartilhada que será utilizado
    work_centroides = centroides[0:num_centroides, :]
    work_data = data[start_row:end_row, :]

    # Soma parcial
    centroides_acumulado = np.zeros((num_centroides, shape_centroides[1]))

    # Loop que será executado enquanto a main não verificar que os centróides não variaram e decidir que acabou a execução
    while True:
        # Faz execução de cálculo da distância dos centróides até os pontos elege ao ponto o seu centróide
        # e de alguma forma faz a soma de cada centróide e envia a main
        for ponto in work_data:
            min_center = None
            min_dist = np.inf
            for index, center in enumerate(work_centroides):
                dist = calcula_dist(ponto, center)
                if dist < min_dist:
                    min_center = index # Se for o atual menor ponto salva o identificador do centroide
                    min_dist = dist
            ponto[-2] = min_center # Atribui à coluna de centroide dos dados a qual centroide pertence atualmente

            for i in range(shape_centroides[1] - 1):
                centroides_acumulado[min_center, i] += ponto[i] # Soma valor da coluna i do dado a coluna i do centroide a ser atualizado
            # Contabiliza também que mais um dado foi somado àquele centroide
            centroides_acumulado[min_center, -1] += 1

            # Jogar valores no acumulado da Main
        with lock_soma:
            for i in range(num_centroides, shape_centroides[0]): # Percorre no bloco de linhas de baixo
                for j in range(shape_centroides[1]): # Percorre toda a coluna dos centroides
                    shift_linha = i - num_centroides
                    centroides[i, j] += centroides_acumulado[shift_linha, j] # Soma valor da coluna i do dado a coluna i do centroide a ser atualizado
                    centroides_acumulado[shift_linha, j] = 0
        # Fim da rodada para os calculadores

        # A cada processo que termina sua execução, incrementa o contador de processos
        with lock:  # Garante que o incremento do contador seja atômico
            counter.value += 1
            #print(f"Processo {process_id} terminou uma rodada")

            # Quando o último processo incrementar, avisa a main para desbloquear
            if counter.value == num_processos:
                counter.value = 0
                sem_m.release()  # Avisa a main para executar seu código

        # Espera até que a main decida e libere a execução
        sem_c.acquire()
        
        # Verifica se a main determinou que os processos devem parar
        if stop_condition.value == 1:
            #print(f"Processo {process_id} interrompido por condição de parada.")
            break


def calcula_dist(p1, p2):
    """
    :param p1: primeiro ponto
    :param p2: segundo ponto
    :return: distância entre o primeiro e segundo ponto
    """
    soma = 0
    # Percorre todas os valores das colunas dos dados do dataset
    for i in range(p2.shape[0] - 1):
        soma += (p1[i] - p2[i]) ** 2

    return soma ** (1/2)