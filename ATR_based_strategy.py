# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 21:20:31 2022

@author: DELL
"""

# =============================================================================
# ATR based stratigy
# If value goes below ATR buy/Long, close position when price reach ATR
# and sell/Short when goes higher than ATR, close position when price reach ATR
# =============================================================================

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from time import time

X_candle_high = 3
Y_candle_high = 3
n_average_TR = 20


file_name = "Data_OHLC.csv"
df_data = pd.read_csv(file_name, index_col=1,parse_dates=['Date'])
df_data.drop(['S No.'],axis=1,inplace=True)

# =============================================================================
# 'X_candles_high' column will have the high of X days High
# Eg. X = 3; fill the data from 4th row: which make sure we are using historical data, not future data
# =============================================================================

df_data['X_candles_high'] = df_data['HIGH'].rolling(X_candle_high).max().shift(1)
df_data['Y_candles_low'] = df_data['LOW'].rolling(Y_candle_high).min().shift(1)
df_data.info()
df_true_range = pd.DataFrame()
df_true_range['H-L'] = df_data['HIGH']-df_data['LOW']
df_true_range['H-PLP'] = df_data['HIGH']-df_data['LAST_PRICE'].shift(1)
df_true_range['PLP-L'] = df_data['LAST_PRICE'].shift(1)-df_data['LOW']
df_data['True_Range'] = df_true_range[['H-L','H-PLP','PLP-L']].max(axis=1,skipna=False).shift(1)

df_data['ATR'] = np.nan
ATR_loc = n_average_TR+df_data['True_Range'].isna().sum()
df_data['ATR'].iloc[ATR_loc-1] = df_data['True_Range'].iloc[df_data['True_Range'].isna().sum():ATR_loc].mean()

for i in range(ATR_loc,len(df_data)):
    df_data['ATR'].iloc[i] = (df_data['ATR'].iloc[i-1] *(n_average_TR-1) + df_data['True_Range'].iloc[i])/n_average_TR

df_data['Signal']= np.where(df_data['HIGH']>=df_data['X_candles_high'],'Buy',\
                             np.where(df_data['LOW']<=df_data['Y_candles_low'],'Sell', np.nan))

df_data['Signal'].replace('nan',np.nan,inplace=True)
df_data.loc[df_data['ATR'].isna(),'Signal'] = np.nan

df_data['Signal_price'] = np.where(df_data['Signal']=='Buy',df_data['X_candles_high'],\
                                   np.where(df_data['Signal']=='Sell',df_data['Y_candles_low'], np.nan))
df_data['Entry Rep'] = np.nan
for i in range(len(df_data['Signal'])):    
    if df_data['Signal'].iloc[i]==df_data['Signal'].shift(1).iloc[i]:
        df_data.loc[df_data.index[i],'Entry Rep'] = df_data['Entry Rep'].iloc[i-1]
    elif ((df_data['Signal'].iloc[i]=='Buy')| (df_data['Signal'].iloc[i]=='Sell')):
        df_data.loc[df_data.index[i],'Entry Rep'] = df_data['Signal_price'].iloc[i]
    else:
        df_data.loc[df_data.index[i],'Entry Rep'] = np.nan
