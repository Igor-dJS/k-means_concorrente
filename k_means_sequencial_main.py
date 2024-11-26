import sys
import os
import numpy as np
import pandas as pd
import time
from k_means_sequencial import *

def main():
    if len(sys.argv) < 3:
        print("Uso: python k_means_concorrente_main.py <dataset_path> <n_clusters> [<output_log>](opcional)")
        return

    dataset_path = sys.argv[1]
    n_clusters = int(sys.argv[2])
    num_processos = 0  # Pois é sequencial
    output_log = sys.argv[3] if len(sys.argv) > 3 else None

    # Leitura do dataset
    df = pd.read_csv(dataset_path, delimiter=",")
    df = df.reset_index(drop=False)
    list_col = None

    # Verifica se é o dataset de Iris com base no nome do arquivo ou estrutura esperada
    iris_columns = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
    if all(col in df.columns for col in iris_columns):
        # Usa colunas especificadas do dataset Iris em iris_columns
        list_col = iris_columns.copy()
    else:
        # usa todas as colunas do dataset para o cálculo
        # dataset com quantidade padrão de colunas gerada (pode ser alterado no script python de geração de dados de teste)
        list_col = df.columns.tolist()

    list_col.append("index")
    data = df[list_col].to_numpy()

    # Executa o k-means sequencial e calcula o tempo de processamento
    inicio = time.time()
    result = k_means(n_clusters, data)
    fim = time.time()
    delta = fim - inicio

    #print(f"Tempo de processamento: {delta:.5f} segundos")

    # Salvar processos, pontos e tempo de processamento no arquivo output_log, se fornecido
    if output_log:
        log_data = {'Quantidade de Processos': [num_processos], 'Quantidade de Pontos': [len(data)], 'Tempo de Processamento': [round(delta, 5)]}
        df_log = pd.DataFrame(log_data)

        if not os.path.exists(output_log):
            df_log.to_csv(output_log, header=False, index=False)  # Cria arquivo de log caso não exista
        else:
            df_log.to_csv(output_log, mode='a', header=False, index=False)

    # Salvar csv da posição dos centróides
    centroides = list(result.keys())
    list_col_centroides = list_col.copy()
    list_col_centroides.remove("index")
    df_centroides = pd.DataFrame(centroides, columns=list_col_centroides)
    if not os.path.exists("./logs/Sequencial"):
        os.makedirs("./logs/Sequencial")
    df_centroides.to_csv(f"./logs/Sequencial/k_{n_clusters}_centers", index = False)
        
    # Salvar csv dos dados com seu index e centróide a qual pertence
    list_dataframes = []
    value_centroide = 0
    for key in result.keys():
        df_ = pd.DataFrame(result[key], columns=list_col)
        df_["centroide"] = value_centroide
        df_["index"] = df_["index"].astype(int)
        list_dataframes.append(df_)
        value_centroide += 1

    df_concatenado = pd.concat(list_dataframes, ignore_index=True)
    df_concatenado.to_csv(f"./logs/Sequencial/k_{n_clusters}_data", index = False)
    
if __name__ == '__main__':
    main()
