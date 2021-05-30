#!/usr/bin/env python
# coding: utf-8

# # Resultados de teste do robot Caixote, desde o início do ano

# Conecta com MetaTrader

# In[2]:


############################################
# Init: setup, imports and connects to MT5 #
############################################

# específico para jupyter notebook
# get_ipython().run_line_magic('matplotlib', 'inline')
# %matplotlib notebook

import numpy as np
import MetaTrader5 as mt5
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# plt.ion() #descomentar para usar gráficos interativos

# configs
pd.set_option('display.max_columns', 500)  # number of columns to be displayed
pd.set_option('display.width', 1500)      # max table width to display
# display data on the MetaTrader 5 package // exibe dados do MT5
print("MetaTrader5 package author: ", mt5.__author__)
print("MetaTrader5 package version: ", mt5.__version__)
print()
# establish connection to the MetaTrader 5 terminal // tenta conectar com MT5 ou quit
if not mt5.initialize():
    print("initialize() falhou, código de erro =", mt5.last_error())
    quit()
print("Conectado com sucesso")


# ## Busca os dados de negociações
#
# Define as datas de inicio e fim da busca.

# In[3]:


# get deals from/to dates and show number of deals
from_date = datetime(2020, 1, 1)
to_date = datetime.now()
#to_date = datetime(2021, 5, 5)


# Realiza consulta de negociações e exibe o número de negócios no período ou mensagem de erro se não achar nada

# In[4]:


# recebe negócios com datas de from_date até to_date
deals = mt5.history_deals_get(from_date, to_date)

# deals # <-- descomentar para ver os dados raw das operações
if deals == None:
    print("Nenhum negócio encontrado, código de erro={}" . format(mt5.last_error()))
    quit()
elif len(deals) > 0:
    print("Houve", len(deals), "negócios desde",  from_date, "até", to_date)


# Exibe os dados de negociações consultadas

# In[5]:


# list deals one by own // descomenta as próximas 3 linhas
# print("Exibindo negócios um a um: ", len(deals))
# for deal in deals:
#    print(" ",deal) # mostra cada negócio realizado do jeito que vem


# Cria o Data Frame

# In[6]:


# create dataFrame from deals and add some columns
print("Cria dataFrame de:", len(deals), "negócios")
# display these deals as a table using pandas.DataFrame
df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())


# Prepara os dados

# In[7]:


# insert readable datetime column // transforma em data legível
df['time'] = pd.to_datetime(df['time'], unit='s')


# **Normalizar valores das operações**
#
# Se for ação, reduz volume a um lote (100 unidades) e ajusta o valor
#
# Se for indice, reduz volume a uma unidade e ajusta o valor
#

# In[8]:


df['newProfit'] = np.where(df["symbol"].str.slice(0, 3) == "WIN",
                           df["profit"] / df["volume"],
                           df["profit"] / (df["volume"] / 100))


# Remove colunas não utilizadas

# In[9]:


# remove unused columns
# df.drop(["external_id", "magic", "swap", "commission", "fee", "price", "ticket", "order", "time_msc", "type", "entry", "position_id", "reason", "comment"], inplace=True, axis=1)
# DEBUG: mostra resultado #df.head(20)


# Agrupa e acumula os resultados por ativo

# In[10]:


# acumula profit agrupado por símbolo
df["amount"] = df.groupby(["symbol"]).newProfit.cumsum()


# Debug: Exibe uma amostra dos dados tratados e acumulados para conferência

# In[11]:


# DEBUG: mostra resultado # df.head(20)


# Agrupa os dados por Ativo e mostra o número de negócios por ativo

# In[12]:


dfg = df.groupby("symbol")
dfg.count().profit


# Plota os dados

# In[13]:


# iterage com cada item do grupo para personalizar o ylabel
for name, group in dfg:
    group.plot(x='time', y='amount', ylabel=name, legend=False)

plt.show()


# In[14]:


# iterage com o grupo para exibir todas as curvas no mesmo gráfico
fig, ax = plt.subplots(figsize=(30, 10))
for name, group in dfg:
    group.plot(x='time', y='amount', ax=ax, label=name)
plt.show()


# In[ ]:
