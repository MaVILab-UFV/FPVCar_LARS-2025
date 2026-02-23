import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 
PATH_FILE = 'tests/distancia/data/tests-ok-2.csv'

def box_plot_latencia():
    dados = pd.read_csv(PATH_FILE)
    # filtra os primeiros 50
    dados = dados[dados['sample'] > 50]
    
    dados.boxplot(column='latencia', by='distancia', grid=False)
    
    # Configurando os ticks do eixo y com precisão decimal
    ticks = np.arange(0, 0.21, 0.01)  # Valores de ticks com intervalo de 0.2
    plt.yticks(ticks, [f"{tick:.2f}" for tick in ticks])  # Formata para duas casas decimais
    
    plt.title(f"Boxplot de 'Latência' por 'Distância'")
    plt.suptitle("")
    plt.xlabel('Distância (m)')
    plt.ylabel('Latência (s)')
    plt.show()

def box_plot_fps():
    dados = pd.read_csv(PATH_FILE)
    # filtra os primeiros 50
    dados = dados[dados['sample'] > 50]
    
    dados.boxplot(column='fps', by='distancia', grid=False)
    
    # Configurando os ticks do eixo y com precisão decimal
    ticks = np.arange(0, 10.1, 0.5)  # Valores de ticks com intervalo de 0.2
    plt.yticks(ticks, [f"{tick:.2f}" for tick in ticks])  # Formata para duas casas decimais
    
    plt.title(f"Boxplot de 'FPS' por 'Distância'")
    plt.suptitle("")
    plt.xlabel('Distância (m)')
    plt.ylabel('FPS')
    plt.show()
    
def box_plot_latencia_all():
    dados = pd.read_csv(PATH_FILE)
    # filtra os primeiros 50
    dados = dados[dados['sample'] > 50]
    
    dados.boxplot(column='latencia', grid=False)
    
    # Configurando os ticks do eixo y com precisão decimal
    ticks = np.arange(0, 0.11, 0.01)  # Valores de ticks com intervalo de 0.2
    plt.yticks(ticks, [f"{tick:.2f}" for tick in ticks])  # Formata para duas casas decimais
    
    plt.title(f"Boxplot de 'Latência'")
    plt.suptitle("")
    # plt.xlabel('Distância (m)')
    plt.ylabel('Latência (s)')
    plt.show()

def box_plot_fps_all():
    dados = pd.read_csv(PATH_FILE)
    # filtra os primeiros 50
    dados = dados[dados['sample'] > 50]
    
    dados.boxplot(column='fps', grid=False)
    
    # Configurando os ticks do eixo y com precisão decimal
    ticks = np.arange(0, 10.1, 0.5)  # Valores de ticks com intervalo de 0.2
    plt.yticks(ticks, [f"{tick:.2f}" for tick in ticks])  # Formata para duas casas decimais
    
    plt.title(f"Boxplot de 'FPS'")
    plt.suptitle("")
    # plt.xlabel('Distância (m)')
    plt.ylabel('FPS')
    plt.show()

plt.rc('font', size=20)  # Altera o tamanho geral da fonte

box_plot_fps()
box_plot_latencia()
box_plot_fps_all()
box_plot_latencia_all()