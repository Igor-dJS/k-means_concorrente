import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from k_means_sequencial import *
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
        end = False
        list_col = []
        # d1,okPressed1=QInputDialog.getText(self, "Arquivo", "Caminho")
        # d2,okPressed2=QInputDialog.getInt(self, "Centroides", "Qtde:")
        
        # while(not end):
        #     d4,okPressed4=QInputDialog.getText(self, "Nova Coluna", "Nome")

        #     if d4 == "" and okPressed4:
        #         end = True
        #     else:
        #         list_col.append(d4)

        okPressed1 = True
        okPressed2 = True
        d1 = "./datasets/Iris.csv"
        d2 = 3
        list_col = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm"]

        if okPressed1 and okPressed2:
            df = pd.read_csv(d1, delimiter="," )

            df = df.reset_index(drop=False)
            list_col.append("index")
            data = df[list_col].to_numpy()

            result = k_means(d2, data)

            # Salvar csv da posição dos centróides 
            centroides = list(result.keys())
            list_col_centroides = list_col.copy()
            list_col_centroides.remove("index")
            df_tmp = pd.DataFrame(centroides,  columns = list_col_centroides)
            df_tmp.to_csv(f"./logs/Sequencial/k_{d2}_centers", index = False)

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
            df_concatenado.to_csv(f"./logs/Sequencial/k_{d2}_data", index = False)

            


if __name__=='__main__':
    app=QApplication(sys.argv)
    ex=App()