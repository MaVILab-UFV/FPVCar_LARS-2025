import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 
PATH_FILE = 'tests/distancia/data/test_01m.csv'
PATH_FILE_OUTPUT = 'tests/distancia/data/test)01m_process.csv'

df = pd.read_csv(PATH_FILE)

size = df.shape[0]

a = [i%151 + 1 for i in range(size)]

df['sample'] = a

print(df)

df.to_csv(PATH_FILE_OUTPUT, index=False)
