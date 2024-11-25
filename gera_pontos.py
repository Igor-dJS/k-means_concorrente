import sys
import numpy as np
import pandas as pd

def gera_pontos_csv(qtd_pontos, output_file):
    """
    Gera um conjunto de pontos aleatórios com 4 colunas e salva em formato CSV.

    Args:
        qtd_pontos (int): Quantidade de pontos a serem gerados.
        output_file (str): Nome do arquivo CSV de saída.
    """
    # Gera uma matriz com qtd_pontos linhas e 4 colunas, com valores entre 0 e 10
    dados = np.random.uniform(0, 10, (qtd_pontos, 4))
    
    # Converte para DataFrame para salvar em CSV
    df = pd.DataFrame(dados, columns=["Coluna1", "Coluna2", "Coluna3", "Coluna4"])
    df.to_csv(output_file, index=False)
    print(f"Arquivo '{output_file}' gerado com {qtd_pontos} pontos.")

if __name__ == "__main__":
    # Verifica se os argumentos necessários foram passados
    if len(sys.argv) != 3:
        print("Uso: python gera_pontos.py <quantidade_pontos> <arquivo_saida>")
        sys.exit(1)
    
    try:
        # Lê os argumentos
        qtd_pontos = int(sys.argv[1])
        output_file = sys.argv[2]

        # Gera os pontos e salva no arquivo CSV
        gera_pontos_csv(qtd_pontos, output_file)
    except ValueError:
        print("Erro: A quantidade de pontos deve ser um número inteiro.")
        sys.exit(1)
