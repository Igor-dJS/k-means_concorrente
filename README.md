# **K-Means: Implementação Sequencial e Concorrente**

Este projeto foi desenvolvido como parte de um projeto final de implementação da disciplina  **Programação Concorrente** na Universidade Federal do Rio de Janeiro. Ele explora o uso do algoritmo de agrupamento **K-Means** em duas implementações: sequencial e concorrente, avaliando seu desempenho em diferentes tamanhos de datasets.

## **Descrição do Algoritmo K-Means**

O K-Means é um algoritmo de aprendizado de máquina que organiza dados em **k** grupos com base em suas similaridades. Ele utiliza os seguintes passos:

1. Escolha inicial dos centróides;
2. Atribuição de pontos ao centróide mais próximo;
3. Atualização dos centróides;
4. Repetição até a convergência.

Na versão concorrente, utilizamos o módulo `multiprocessing` para paralelizar as etapas que envolvem cálculos independentes, como a atribuição de pontos e atualização dos centróides, mitigando o impacto do **GIL** do Python.

## **Estrutura do Projeto**

* **`gera_pontos.py`** : Gera datasets personalizados com diferentes tamanhos de linhas e colunas para geração de logs para análise de desempenho.
* **`k_means_sequencial.py`** : Implementação da função de execução do K-Means sequencial.
* **`k_means_concorrente.py`** : Implementação da função executada pelos processos no K-Means concorrente.
* **`k_means_sequencial_main.py`** : Algoritmo principal para execução do K-Means sequencial.
* **`k_means_concorrente_main.py`** : Algoritmo principal para execução do K-Means concorrente.
* **`notebook_analise_desempenho.ipynb`** : Notebook com geração de tabelas e gráficos para análise de desempenho.
* **`geraTemposKMeans.sh`** : Script para gerar os tempos médios de execução e salvar em arquivos de logs para análise.

## Requisitos e Instalação

Este projeto utiliza as seguintes bibliotecas para sua execução:

* **NumPy** : Manipulação eficiente de arrays e operações matemáticas.
* **Pandas** : Análise e manipulação de dados estruturados.
* **Matplotlib** : Criação de gráficos e visualizações.
* **Seaborn** : Visualizações estatísticas aprimoradas e estilizadas.

#### Como instalar

1. Certifique-se de ter **Python 3.7 ou superior** instalado.
2. Instale as dependências com o comando:

   `pip install numpy pandas matplotlib seaborn`

Ou utilize o arquivo `requirements.txt` para instalação:

`pip install -r requirements.txt`

### **Diretórios**

* **`./datasets/`** : Contém os arquivos de datasets gerados com diferentes quantidades de pontos, organizados por instâncias(linhas) e atributos(colunas).
* **`./logs/`** : Contém os arquivos de log das execuções do K-Means sequencial e concorrente. Os logs são organizados conforme os parâmetros de clusters e atributos.

## **Como Utilizar**

### **Gerar Dataset**

O script `gera_pontos.py` é utilizado para gerar datasets personalizados. Para isso, execute o seguinte comando:

```bash
python gera_pontos.py <quantidade_pontos> <quantidade_colunas> <arquivo_saida>
```

* **`<quantidade_pontos>`** : Número de pontos (linhas) do dataset (ex.: 500, 1000, 10000, etc.).
* **`<quantidade_colunas>`** : Número de atributos (colunas) para cada ponto de dados (ex.: 3, 4, 8, 16, etc.).
* **`<arquivo_saida>`** : Nome do arquivo onde o dataset será salvo (ex.: `dataset_500.csv`, `dataset_1000.csv`).

---

### **Executar o Algoritmo K-Means Sequencial**

Para executar o algoritmo K-Means na versão sequencial, utilize o comando:

```
python k_means_sequencial_main.py <dataset_path> <n_clusters> <output_log>(opcional)
```

* **`<dataset_path>`** : Caminho para o dataset gerado (ex.: `./datasets/3_clusters_4_attributes/dataset_1000.csv`).
* **`<n_clusters>`** : Número de clusters a serem formados (ex.: 2, 3, 4, 5, 10, etc).
* **`<output_log>`** (opcional): Caminho para o arquivo de log onde os tempos de execução podem ser salvos.

**Observação** : Caso você não queira salvar o log, o parâmetro `<output_log>` é opcional. Para isso, basta omitir o argumento de log no comando.

---

### **Executar o Algoritmo K-Means Concorrente**

Para executar o algoritmo K-Means na versão concorrente, utilize o comando:

```
python k_means_concorrente_main.py <dataset_path> <n_clusters> <num_processos> <output_log>(opcional)
```

* **`<dataset_path>`** : Caminho para o dataset gerado (ex.: `./datasets/3_clusters_4_attributes/dataset_1000.csv`).
* **`<n_clusters>`** : Número de clusters a serem formados (ex.: 2, 3, 4, 5, 10, etc).
* **`<num_processos>`** : Número de processos paralelos a serem utilizados na versão concorrente (ex.: 2, 4, 8).
* **`<output_log>`** (opcional): Caminho para o arquivo de log onde os tempos de execução podem ser salvos.

 **Observação** : Caso você não queira salvar o log, o parâmetro `<output_log>` é opcional. Para isso, basta omitir o argumento de log no comando.

## **Gerar Dados de Execução para Análise de Desempenho**

O script `geraTemposKMeans.sh` automatiza a execução dos algoritmos K-Means (sequencial e concorrente) para diferentes configurações e salva os tempos de execução. Para executá-lo, basta rodar o seguinte comando:

```
bash geraTemposKMeans.sh
```

Esse comando irá gerar os datasets, executar o K-Means sequencial e concorrente para diferentes quantidades de pontos e processos, e salvar os logs em arquivos CSV no diretório de logs (ex.: `./logs/log_execucao_kmeans_3_clusters_8_attributes.csv`).

## **Testes de Corretude**

### **Descrição**

Para verificar a corretude entre as versões sequencial e concorrente, utilizou-se o conjunto de dados **Iris** . O algoritmo de comparação foi implementado no notebook  **`logs/compare.ipynb`** , onde são analisadas as diferenças entre os resultados dos dois métodos.

### **Casos de Teste**

* **Dataset** : Iris
  **Número de Centróides** : 3
  **Número de Processos** : 8
  **Resultado** : Os resultados foram iguais, com pequenas variações nos centróides do concorrente.
* **Dataset** : Iris
  **Número de Centróides** : 4
  **Número de Processos** : 8
  **Resultado** : Centróides do concorrente muito próximos ao sequencial, mas com pequenas diferenças.
* **Dataset** : Iris
  **Número de Centróides** : 3
  **Número de Processos** : 4
  **Resultado** : Igualdade nos resultados.
* **Dataset** : Iris
  **Número de Centróides** : 4
  **Número de Processos** : 4
  **Resultado** : Igualdade nos resultados.

### **Conclusão**

Embora o programa concorrente possa apresentar pequenas variações nos centróides devido a limitações de precisão numérica, os resultados geralmente estão em conformidade com a versão sequencial. O algoritmo concorrente foi considerado correto, com pequenas diferenças esperadas por limitações computacionais.

### **Como Realizar a Verificação de Corretude**

Para realizar a verificação de corretude, execute o notebook  **`logs/compare.ipynb`** , que compara os resultados sequenciais e concorrentes, verificando a atribuição correta dos pontos aos centróides.

## **Análise de Desempenho**

Para analisar o desempenho dos algoritmos sequencial e concorrente, utilize o notebook **`logs/analise_log_execucao_kmeans.ipynb`** . Este notebook processa os logs gerados pelo script **`geraTemposKMeans.sh`** e gera tabelas e gráficos para avaliar o **tempo de processamento** , **aceleração** e **eficiência** dos algoritmos.

### **Bibliotecas Utilizadas**

O notebook faz uso das seguintes bibliotecas para manipulação de dados e visualização:

* **Pandas** : Para manipulação de dados e criação de DataFrames.
* **Matplotlib** : Para geração de gráficos estáticos.
* **Seaborn** : Para criar visualizações mais avançadas e com maior impacto visual.
* **NumPy** : Para operações numéricas e cálculos rápidos.

### **O que o Notebook Faz**

* **Leitura de Logs** : O notebook utiliza os logs salvos durante as execuções para calcular o tempo de processamento de cada execução.
* **Cálculo de Aceleração** : Mede a aceleração obtida na versão concorrente em comparação com a versão sequencial.
* **Cálculo de Eficiência** : Avalia a eficiência do uso de múltiplos processos na versão concorrente.
* **Geração de Tabelas** : O notebook também gera tabelas com os resultados numéricos para facilitar a análise dos dados de desempenho.
* **Geração de Gráficos** : O notebook gera gráficos que ilustram o desempenho dos algoritmos para diferentes tamanhos de dataset e números de processos.
