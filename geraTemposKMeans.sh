#!/bin/bash

quantidadeExecucoes=5

# Configurações dos testes
quantidadePontos=("500" "1000" "10000" "100000")  # Quantidades de pontos nos conjuntos de dados
quantidadeProcessos=("1" "2" "4" "8")    # Quantidades de processos a serem testadas
n_clusters=3

# Geração de arquivos CSV para cada quantidade de pontos
# TODO: Implementar geração com opção de determinar a quantidade de colunas
#for pontos in "${quantidadePontos[@]}"; do
#    echo "Gerando arquivo de dados com $pontos pontos..."
#    python gera_pontos.py $pontos "./datasets/dataset_${pontos}.csv"
#done

# Execução do K-Means sequencial
for pontos in "${quantidadePontos[@]}"; do
    for i in $(seq 1 $quantidadeExecucoes); do
        echo "Execução Sequencial - Dataset com $pontos pontos (Execução $i)..."
        python k_means_sequencial_main.py "./datasets/dataset_${pontos}.csv" $n_clusters "./logs/log_execucao_kmeans.csv"
    done
done

# Execução do K-Means concorrente com diferentes números de processos
for processos in "${quantidadeProcessos[@]}"; do
    for pontos in "${quantidadePontos[@]}"; do
        for i in $(seq 1 $quantidadeExecucoes); do
            echo "Execução Concorrente - Dataset com $pontos pontos e $processos processo(s) (Execução $i)..."
            python k_means_concorrente_main.py "./datasets/dataset_${pontos}.csv" $n_clusters $processos "./logs/log_execucao_kmeans.csv"
        done
    done
done

echo "Geração de dados para testes concluída."
