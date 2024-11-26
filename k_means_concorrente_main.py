import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from multiprocessing import (Process, Semaphore, Value, Lock, Event)
from k_means_concorrente import *
from PyQt5.QtWidgets import QApplication,QWidget,QInputDialog

# Variáveis
num_processos = 8
sem_m = Semaphore(0) # Semáforo para controle da main esperar os processos
sem_c = Semaphore(0) # Semáforo para os processos esperarem a main liberá-los para próxima rodada, verificando antes a stop_condition
lock = Lock() # Lock para garantir que o contador é atualizado de forma atômica
lock_soma = Lock() # Lock para garantir que os processos não terão condição de corrida nos dados dos centroides sendo atualizados
counter = Value('i', 0)  # Contador de processos que terminaram a rodada
stop_condition = Value('i', 0)  # Condição de parada
c = 0 # Contador de iterações/rodadas do algoritmo


class App(QWidget):
    # Define as configurações das janelas 
    def __init__(self):
        super().__init__()
        self.title='K-mean clustering'
        self.left=10
        self.top=10
        self.width=300
        self.height=250
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.getText()
        self.show()
    def getText(self):
        global c
        end = False
        list_col = []
        # d1,okPressed1=QInputDialog.getText(self, "Arquivo", "Caminho") # Caminho do arquivo csv com os dados
        # d2,okPressed2=QInputDialog.getInt(self, "Centroides", "Qtde:") # Obtém número de clusters/centróides
        
        # while(not end):
        #     d4,okPressed4=QInputDialog.getText(self, "Nova Coluna", "Nome")

        #     if d4 == "" and okPressed4:
        #         end = True
        #     else:
        #         list_col.append(d4)

        # Código temporário apenas para facilitar testes
        # Posteriormente descomentar linhas de código acima e excluir esse trecho
        okPressed1 = True
        okPressed2 = True
        d1 = "./datasets/Iris.csv"
        d2 = 4
        list_col = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm"]

        if okPressed1 and okPressed2:
            # Ler csv com pandas
            df = pd.read_csv(d1, delimiter="," )

            # Transforma o index em uma coluna também para rastrear posteriormente as instâncias e converte para numpy array
            df["centroide"] = 0
            df = df.reset_index(drop=False)
            list_col.append("centroide")
            list_col.append("index")
            data = df[list_col].to_numpy()

            # Num de linhas
            num_linhas = data.shape[0]

            # Obtém os centróides iniciais utilizando as primeiras linhas e ignorando a coluna de index (centróides não são instâncias) e a qual centroide pertence
            # Além disso temos o dobro de linhas onde o segundo bloco de linhas será utilizado para cálculo da próxima rodada com a nova
            # posição dos centróides
            tuple_zeros = tuple(0 for i in range(len(list_col) - 1))

            list_for_centers = [tuple(data[i, :-1]) for i in range(d2)]
            list_for_centers = list_for_centers + [tuple_zeros for i in range(d2)]

            cluster_centers = np.array(list_for_centers)

            # Num cols centroides
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


            processos = []
            # Cria e dispara os processos
            for i in range(num_processos):
                start_row = i * step
                end_row = (i + 1) * step if (i < num_processos - 1) else num_linhas
                p = Process(target=Calculadores, 
                            args=(i, shm1.name, shm2.name, cluster_centers.shape, data.shape, cluster_centers.dtype, data.dtype, start_row, end_row, num_processos, d2, lock, lock_soma, counter, sem_m, sem_c, stop_condition))
                processos.append(p)
                p.start()


            while stop_condition.value == 0:
                # Main Aguardando todos os processos completarem a rodada.
        
                # Espera até que o último processo avise a main
                sem_m.acquire()

                # Atualizar valor dos novos centroides
                for i in range(d2, 2*d2):
                    for j in range(num_cols_centroides - 1):
                         shared_array1[i, j] = round(shared_array1[i, j] / shared_array1[i, -1], 5)

                # Verifica se os centroides atualizados são iguais aos anteriores
                change_flag = False
                for i in range(0, d2):
                    for j in range(num_cols_centroides - 1):
                        if shared_array1[i, j] != shared_array1[i+d2, j]:
                            change_flag = True
                            break
                    if change_flag:
                        break

                # Se não houve mudança altera a stop_condition
                if change_flag == False:
                    stop_condition.value = 1
                else:
                    # Se houve mudança copia os valores dos centroides atualizados para a parte de cima
                    for i in range(0, d2):
                        for j in range(num_cols_centroides - 1):
                            shared_array1[i, j] = shared_array1[i+d2, j]
                            shared_array1[i+d2, j] = 0 # Zera as posições dos centroides
                        shared_array1[i+d2, -1] = 0 # Zera coluna da quantidade de pontos que pertencem ao centroide
                

                c = c + 1 # Conta número de iterações/rodadas que o algoritmo teve
                for i in range(num_processos):
                    sem_c.release()

            # Espera todos os processos terminarem
            for p in processos:
                p.join()

            # Salva csv dos centroides
            df_tmp = pd.DataFrame(shared_array1[:d2,:-1],  columns = list_col[0:-2])
            df_tmp.to_csv(f"./logs/Concorrente/k_{d2}_p_{num_processos}_centers", index = False)

            # Salva csv dos dados com as colunas de qual centroide pertence e seu índice no arquivo original
            df_tmp = pd.DataFrame(shared_array2,  columns = list_col)
            df_tmp.to_csv(f"./logs/Concorrente/k_{d2}_p_{num_processos}_data", index = False)

            # Fechar as referências à memória compartilhada
            shm1.close()  # Fecha a referência ao shm1
            shm2.close()  # Fecha a referência ao shm2

            # Desvincular as memórias compartilhadas para liberar o nome no sistema
            shm1.unlink()  # Desvincula shm1, liberando o nome da memória compartilhada
            shm2.unlink()  # Desvincula shm2, liberando o nome da memória compartilhada

            


if __name__=='__main__':
    app=QApplication(sys.argv)
    ex=App()