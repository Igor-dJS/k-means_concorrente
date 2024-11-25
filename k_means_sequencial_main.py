import sys, os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from k_means_sequencial import *
import time
from PyQt5.QtWidgets import QApplication,QWidget,QInputDialog

class App(QWidget):
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
        
        if len(sys.argv) != 4:
            print("Uso: python k_means_sequencial_main.py <dataset_path> <n_clusters> <output_log>")
            return

        dataset_path = sys.argv[1]
        n_clusters = int(sys.argv[2])
        n_threads = 0  # Pois é sequencial
        output_log = sys.argv[3]
    
        end = False
        list_col = []
        '''
        dataset_path,okPressed1=QInputDialog.getText(self, "Arquivo", "Caminho")
        n_clusters,okPressed2=QInputDialog.getInt(self, "Centroides", "Qtde:")

        while(not end):
            d4,okPressed4=QInputDialog.getText(self, "Nova Coluna", "Nome")

            if d4 == "" and okPressed4:
                end = True
            else:
                list_col.append(d4)
        '''

        # Código temporário apenas para facilitar testes
        # Posteriormente descomentar linhas de código acima e excluir esse trecho
        okPressed1 = True
        okPressed2 = True
        #dataset_path = "./datasets/Iris.csv"
        #n_clusters = 3
        #list_col = ["SepalLengthCm", "SepalWidthCm"] #, "PetalLengthCm", "PetalWidthCm"]

        if okPressed1 and okPressed2:
            df = pd.read_csv(dataset_path, delimiter=",")

            df = df.reset_index(drop=False)
            list_col = df.columns.tolist() #pega todas colunas do csv de dados criado, pois é definido com uma quantidade padrão de colunas (pode ser alterado no script de geração de dados)
            list_col.append("index")
            data = df[list_col].to_numpy()

            # executa kmeans sequencial e calcula tempo de processamento
            inicio = time.time()
            result = k_means(n_clusters, data)
            fim = time.time()
            delta = fim - inicio

            #print(f"Tempo de processamento: {delta}")

            # Salvar threads, pontos e tempo de processamento em um arquivo CSV
            log_data = {'Quantidade de Threads': [n_threads], 'Quantidade de Pontos': [len(data)], 'Tempo de Processamento': [round(delta, 5)]}
            df_log = pd.DataFrame(log_data)

            if not os.path.exists(output_log):
                df_log.to_csv(output_log, header=False, index=False) # Cria arquivo de log caso não exista
            else:
                df_log.to_csv(output_log, mode='a', header=False, index=False)

            # Salvar csv da posição dos centróides
            centroides = list(result.keys())
            list_col_centroides = list_col.copy()
            list_col_centroides.remove("index")
            df_tmp = pd.DataFrame(centroides,  columns = list_col_centroides)
            df_tmp.to_csv("./logs/Sequencial/log0", index = False)

            # Salvar csv dos dados com seu index e centróide a qual pertence
            list_dataframes = []
            value_centroide = 0
            for key in result.keys():
                df_ = pd.DataFrame(result[key], columns = list_col)
                df_["centroide"] = value_centroide
                df_['index'] = df_['index'].astype(int)
                list_dataframes.append(df_)
                value_centroide += 1

            df_concatenado = pd.concat(list_dataframes, ignore_index=True)
            df_concatenado.to_csv("./logs/Sequencial/log1", index = False)

if __name__=='__main__':
    app=QApplication(sys.argv)
    ex=App()