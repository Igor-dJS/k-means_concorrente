import sys
import os
import numpy as np
import pandas as pd
from multiprocessing import Process, Semaphore, Value, Lock
from multiprocessing import shared_memory  # Adicionado para uso de memória compartilhada
from k_means_concorrente import *
import time

# Variáveis Globais
sem_m = Semaphore(0)  # Semáforo para controle da Main esperar os processos
sem_c = Semaphore(0)  # Semáforo para os processos esperarem a main liberá-los para próxima iteração, verificando antes a stop_condition
lock = Lock()          # Lock para garantir que o contador de processos terminados na iteração é atualizado de forma atômica
lock_soma = Lock()     # Lock para garantir que os processos não terão condição de corrida nos dados dos centroides sendo atualizados
counter = Value('i', 0)        # Contador de processos que terminaram a iteração
stop_condition = Value('i', 0) # Condição de parada da Main para comunicar os processos

def main():
    # Controle dos argumentos
    if len(sys.argv) < 4:
        print("Uso: python k_means_concorrente_main.py <dataset_path> <n_clusters> <num_processos> <output_log>(opcional)")
        return
    
    # Lê dados da linha de comando
    dataset_path = sys.argv[1]
    n_clusters = int(sys.argv[2])
    num_processos = int(sys.argv[3])  # Número de processos concorrentes
    output_log = sys.argv[4] if len(sys.argv) > 4 else None

    list_col = None

    # Leitura do dataset
    df = pd.read_csv(dataset_path, delimiter=",")
    
    # Verifica se é o dataset de Iris com base no nome do arquivo ou estrutura esperada
    iris_columns = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
    if all(col in df.columns for col in iris_columns):
        # Usa colunas especificadas do dataset Iris em iris_columns
        df = df[iris_columns]

    # Transforma o index em uma coluna também para rastrear posteriormente as instâncias e converte para numpy array
    list_col = df.columns.tolist()
    df["centroide"] = 0
    df = df.reset_index(drop=False)
    list_col.append("centroide")
    list_col.append("index")
    data = df[list_col].to_numpy()

    # Número de linhas no dataset
    num_linhas = data.shape[0]

    # Obtém os centróides iniciais utilizando as primeiras linhas e ignorando a coluna de index (centróides não são instâncias e não têm index consequentemente)
    # Além disso temos o dobro de linhas onde o segundo bloco de linhas será utilizado para cálculo da próxima iteração com a nova posição dos centróides
    # Note que nossos centroides têm uma coluna extra que para o primeiro bloco de linha não tem funcionalidade, mas para o segundo tem a finalidade de armazenar
    # A quantidade de pontos que estão associados àquele centroide naquela iteração e é usado pela Main para obter a nova posiçõa do centroide dividindo as colunas
    # Com as somas acumuladas por esse valor
    tuple_zeros = tuple(0 for _ in range(len(list_col) - 1)) # Cria uma tupla de zeros com tamanho para as colunas de do dataset mais uma coluna com a função já descrita acima
    list_for_centers = [tuple(data[i, :-1]) for i in range(n_clusters)] # Utiliza as primeiras linhas do dataset para serem os centroides iniciais
    list_for_centers += [tuple_zeros for _ in range(n_clusters)] # Bloco de baixo começa zerado para receber acumulado posteriormente
    cluster_centers = np.array(list_for_centers)

    # Número de colunas nos centróides
    num_cols_centroides = cluster_centers.shape[1]

    # Criando memória compartilhada para o np array dos centróides
    shm1 = shared_memory.SharedMemory(create=True, size=cluster_centers.nbytes)
    shared_array1 = np.ndarray(cluster_centers.shape, dtype=cluster_centers.dtype, buffer=shm1.buf)
    np.copyto(shared_array1, cluster_centers)  # Copia os dados para a memória compartilhada

    # Cria memória compartilhada para o np array dos dados
    shm2 = shared_memory.SharedMemory(create=True, size=data.nbytes)
    shared_array2 = np.ndarray(data.shape, dtype=data.dtype, buffer=shm2.buf)
    np.copyto(shared_array2, data)  # Copia os dados para a memória compartilhada

    # Calcula a quantidade de linhas para cada processo com divisão inteira. O resto será atribuido ao último processo.
    step = num_linhas // num_processos

    # Pega tempo de inicio do processamento
    inicio = time.time()

    processos = []
    # Cria e dispara os processos
    for i in range(num_processos):
        start_row = i * step
        end_row = (i + 1) * step if (i < num_processos - 1) else num_linhas  # Ultimo processo processa até num_linhas (última linha)
        p = Process(target=Calculadores, 
                    args=(i, shm1.name, shm2.name, cluster_centers.shape, data.shape, cluster_centers.dtype, 
                          data.dtype, start_row, end_row, num_processos, n_clusters, lock, lock_soma, counter, sem_m, sem_c, stop_condition))
        processos.append(p)
        p.start()

    while stop_condition.value == 0:
        # Main aguardando todos os processos completarem a rodada.
        # Espera até que o último processo desbloqueie a Main
        sem_m.acquire()

        # Atualizar valor dos novos centroides no segundo bloco (que acumula os valores para cálculo dos novos centróides com média dos pontos de cada cluster)
        for i in range(n_clusters, 2 * n_clusters):
            for j in range(num_cols_centroides - 1):
                shared_array1[i, j] = round(shared_array1[i, j] / shared_array1[i, -1], 5)

        # Verifica se os centroides atualizados são iguais aos anteriores
        change_flag = False
        for i in range(n_clusters):
            for j in range(num_cols_centroides - 1):
                if shared_array1[i, j] != shared_array1[i + n_clusters, j]:
                    change_flag = True
                    break
            if change_flag:
                break

        if not change_flag:
            # Se não houve mudança, altera a condição de parada
            stop_condition.value = 1
        else:
            # Se houve mudança, copia os valores dos centroides atualizados para a parte de cima
            # assim deixa novos valores calculados para os centróides atualizados no 1* bloco
            for i in range(n_clusters):
                for j in range(num_cols_centroides - 1):
                    shared_array1[i, j] = shared_array1[i + n_clusters, j] # Copia do 2* bloco para o 1* bloco
                    shared_array1[i + n_clusters, j] = 0  # Zera as posições dos centróides das somas das coordenadas
                shared_array1[i + n_clusters, -1] = 0  # Zera coluna da quantidade de pontos que pertencem ao centróide

        # Libera os processos para a próxima rodada
        for _ in range(num_processos):
            sem_c.release()

    # Pega tempo final do processamento e calcula quanto tempo levou
    fim = time.time()
    delta = fim - inicio

    # Salvar processos, pontos e tempo de processamento no arquivo output_log, se fornecido
    if output_log:
        log_data = {'Quantidade de Processos': [num_processos], 'Quantidade de Pontos': [len(data)], 'Tempo de Processamento': [round(delta, 5)]}
        df_log = pd.DataFrame(log_data)

        if not os.path.exists(output_log):
            df_log.to_csv(output_log, header=False, index=False)  # Cria arquivo de log caso não exista
        else:
            df_log.to_csv(output_log, mode='a', header=False, index=False)

    # Espera todos os processos terminarem
    for p in processos:
        p.join()

    # Salva csv dos centroides
    centroides = shared_array1[:n_clusters, :-1]
    df_centroides = pd.DataFrame(centroides, columns=list_col[0:-2])
    if not os.path.exists("./logs/Concorrente"):
        os.makedirs("./logs/Concorrente")
    df_centroides.to_csv(f"./logs/Concorrente/k_{n_clusters}_p_{num_processos}_centers", index = False)

    # Salva csv dos dados com as colunas de qual centroide pertence e seu index no arquivo original
    df_dados = pd.DataFrame(shared_array2, columns=list_col)
    df_dados.to_csv(f"./logs/Concorrente/k_{n_clusters}_p_{num_processos}_data", index = False)

    # Fechar as referências à memória compartilhada
    shm1.close()  # Fecha a referência ao shm1
    shm2.close()  # Fecha a referência ao shm2

    # Desvincular as memórias compartilhadas para liberar o nome no sistema
    shm1.unlink()  # Desvincula shm1, liberando o nome da memória compartilhada
    shm2.unlink()  # Desvincula shm2, liberando o nome da memória compartilhada

if __name__ == '__main__':
    main()
