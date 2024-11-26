import matplotlib.pyplot as plt
import numpy as np

def calcula_dist(p1, p2):
    """
    :param p1: primeiro ponto
    :param p2: segundo ponto
    :return: distância entre o primeiro e segundo ponto
    """
    
    soma = 0
    # percorre todas os valores das colunas menos a do index
    for i in range(p1.shape[0] - 1):
        soma += (p1[i] - p2[i]) ** 2

    return soma ** (1/2)

def k_means(n_clusters, data):
    """
    :param n_clusters: número de clusters
    :param data: dados
    :return: dicionário onde a chave é o centroide e o valor associado os pontos próximos a ele
    """
    
    qtde_cols = data.shape[1] # obtém a quantidade de colunas

    # Obtendo centroides aleatórios
    cluster_centers = set()
    
    # while len(cluster_centers) != n_clusters:
    #     # Aqui são escolhidos "n_clusters" de pontos (instância ou linhas) aleatoriamente para serem os centróides iniciais
    #     # O set é para garantir que pontos que potencialmente sejam sorteados mais de uma vez sejam adicionados mais de uma vez
    #     cluster_centers = set([tuple(data[np.random.randint(0, data.shape[0]), :-1]) for _ in range(n_clusters)])

    # cluster_centers = tuple(cluster_centers)

    # Utilizando os primeiros dados como os primeiros "n_clusters"
    cluster_centers = set([tuple(data[i, :-1]) for i in range(n_clusters)]) #por qual motivo usar os primeiros e não centróides aleatórios?

    # Listas para saber se as médias dos pontos mudaram a cada iteração
    centers_before = None
    centers_after = []
    centers = None

    while centers_before != centers_after:
        centers_before = centers_after

        # Dicionário de pontos por centroides
        # Temos como chave a tupla com os valores 
        centers = dict(zip(cluster_centers, [set() for _ in range(n_clusters)]))

        # Associa cada ponto ao seu centroide mais próximo
        for ponto in data:
            min_center = None
            min_dist = np.inf
            for center in cluster_centers:
                dist = calcula_dist(ponto, center)
                if dist < min_dist:
                    min_center = center
                    min_dist = dist
            centers[min_center].add(tuple(ponto))

        # Cálculo os novos centroides
        centers_after = []
        for center in centers:
            ponto_medio = []
            for i in range(qtde_cols - 1): # verificar se é pra desconsiderar última coluna que é o index!!!!!!!!!!!!!!!!
                soma = sum([col[i] for col in centers[center]]) #
                media = round(soma / len(centers[center]), 5) # arredondadno número da coluna do contreóide em 5 casas decimais
                ponto_medio.append(media)

            centers_after.append(tuple(ponto_medio))

        cluster_centers = tuple(centers_after)

    return centers