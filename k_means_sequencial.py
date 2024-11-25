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

def plotar(data, result, cols):
    if type(list(list(result.values())[0])[0]) == np.int64:
        plt.hlines(1, 1, max(data) + 1)
        plt.xlim(0, max(data) + 1)
        plt.ylim(0.5, 1.5)

        for item in result:
            lista = list(result[item])
            y = np.ones(np.shape(lista))
            plt.plot(lista, y, '|', ms=40)
        plt.axis('off')
        plt.show()
    else:
        # plt.figure(figsize=(12, 12))
        if data.shape[1] == 3:
            ax = plt.axes(projection='3d')
            ax.set_xlabel(cols[0])
            ax.set_ylabel(cols[1])
            ax.set_zlabel(cols[2])
        else:
            plt.xlabel(cols[0])
            plt.ylabel(cols[1])
        for item in result:
            array = np.array(list(result[item]))
            if array.shape[1] == 2:
                plt.scatter(array[:, 0], array[:, 1])
            else:
                ax.scatter(array[:, 0], array[:, 1], array[:, 2])
        centroides = np.array(list(result.keys()))
        if centroides.shape[1] == 2:
            plt.scatter(centroides[:, 0], centroides[:, 1], marker="D",s=60, c="red")
        else:
            ax.scatter(centroides[:, 0], centroides[:, 1], centroides[:, 2],marker="D", s=60, c="red")
        plt.show()
