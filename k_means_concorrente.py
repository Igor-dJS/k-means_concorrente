import numpy as np
from multiprocessing import shared_memory

# Função executada pelos processos criados
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

    # Matriz para guardar soma parcial do cálculo da nova posição dos centroides posteriormente
    centroides_acumulado = np.zeros((num_centroides, shape_centroides[1]))

    # Loop que será executado enquanto a main não verificar que os centróides não variaram e decidir que acabou a execução
    while True:
        # Faz execução de cálculo da distância dos centróides até os pontos e associa ao ponto o centroide mais próximo
        for ponto in work_data:
            min_center = None
            min_dist = np.inf
            for index, center in enumerate(work_centroides):
                dist = calcula_dist(ponto, center) # Calcula distância do ponto ao centroide
                if dist < min_dist:
                    min_center = index # Se for o atual menor ponto salva o identificador do centroide
                    min_dist = dist # Atualiza o valor da atual menor distância
            ponto[-2] = min_center # Atribui à coluna que identifica o centroide a qual o ponto pertence o atual centroide

            # Adiciona o valor dos dados do ponto à linha do centroide a qual ele pertence para manter o acumulado
            for i in range(shape_centroides[1] - 1):
                centroides_acumulado[min_center, i] += ponto[i] # Soma valor da coluna i do dado a coluna i do centroide a ser atualizado
            # Contabiliza também que mais um dado foi somado àquele centroide
            centroides_acumulado[min_center, -1] += 1

        # Jogar valores no acumulado da Main com exclusão mútua por ser uma área que outros processos possivelmente estejam querendo escrever também
        with lock_soma:
            for i in range(num_centroides, shape_centroides[0]): # Percorre no bloco de linhas de baixo que é o espaço dedicado para cálculo da posição dos novos centroides na Main
                for j in range(shape_centroides[1]): # Percorre toda a coluna dos centroides
                    shift_linha = i - num_centroides # Calcula valor da linha referente na matriz de acumulados do processo
                    centroides[i, j] += centroides_acumulado[shift_linha, j] # Soma valor da coluna j do acumulado do centroide a coluna j do centroide i a ser atualizado
                    centroides_acumulado[shift_linha, j] = 0 # Zera os valores no acumulado para próxima iteração
        # Fim da rodada para os calculadores

        # A cada processo que termina sua execução, incrementa o contador de processos com exclusão mútua
        with lock:  # Garante que o incremento do contador seja atômico
            counter.value += 1

            # Quando o último processo incrementar, avisa a Main para se desbloquear e zera o contador de processos terminados na iteração
            if counter.value == num_processos:
                counter.value = 0
                sem_m.release()  # Avisa a main para executar seu código

        # Espera até que a main decida e libere a execução de todos os processos
        sem_c.acquire()
        
        # Verifica se a main determinou que os processos devem parar ou não
        if stop_condition.value == 1:
            break


def calcula_dist(p1, p2):
    """
    :param p1: primeiro ponto
    :param p2: segundo ponto
    :return: distância euclidiana entre o primeiro e segundo ponto
    """
    soma = 0
    # Percorre todas os valores das colunas dos dados do dataset
    for i in range(p2.shape[0] - 1):
        soma += (p1[i] - p2[i]) ** 2

    return soma ** (1/2)