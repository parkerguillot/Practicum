#!/usr/bin/env python
# coding: utf-8

# # MODEL SELECTION AND DATA LOOPING


import pandas as pd
import numpy as np
import seaborn as sns
import datetime as dt
from matplotlib import pyplot
import matplotlib.pylab as plt
#get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib.pylab import rcParams
rcParams['figure.figsize']=10,6
from IPython.display import display, HTML, display_html
import statsmodels as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
import statistics
from sklearn.linear_model import LinearRegression
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import pmdarima as pm
from pmdarima.arima.stationarity import ADFTest
from pmdarima.arima import auto_arima
from math import sqrt
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import statsmodels.api as sm
import os
import weasyprint
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from pandas import ExcelWriter
import xlsxwriter

data = pd.read_csv('ADH.csv')     #PUT YOUR FILE PATH for CSV DATA HERE!!!!!!!!!!!!!!!
data.head(10).append(data.tail(4))
pd.to_datetime(dowbusi['Date'],format='%m/%d/%Y')
tsdow = dowbusi.set_index(pd.DatetimeIndex(dowbusi['Date']))
tsdow = tsdow.drop(columns=['Date'])
tsdow.tail(10)
type(tsdow.index[3])

for i, j in tsdow.iteritems():
    M1_stepwise = None
    forecast = None
    M1_stepwise_rms = None
    ModelComparison = None
    MCdf = None
    dd = None
    y_hat = None
    naive_rms = None
    MCdf = None
    y_hat_avg = None
    simple_avg_rms = None
    print(i)
    train = tsdow['9/1/2016':'2/1/2019']
    val = tsdow['3/1/2019':'8/1/2019']
    #train = trainfull[i]
    #val = valfull[i]

   #GENERATING FORECASTE AND COMPARING USING DIFFERENT MODELS CREATED WITH TRAINING DATA

   #AUTO-ARIMA
    M1_stepwise = pm.auto_arima(train[i], start_p=1, start_q=1,
                             max_p=3, max_q=3, m=12,
                             start_P=0, seasonal=False,
                             d=1, D=1, trace=True,
                             error_action='ignore',  # don't want to know if an order does not work
                             suppress_warnings=True,  # don't want convergence warnings
                             stepwise=True)
   
    forecast = M1_stepwise.predict(n_periods=len(val[i]))
    forecast = pd.DataFrame(forecast,index = val.index,columns=['Prediction'])
    M1_stepwise_rms = round(sqrt(mean_squared_error(val[i],forecast)),3)
    ModelComparison = {'Model':['ARIMA'], 'RMSE':[M1_stepwise_rms], 'AIC':[M1_stepwise.aic()]}
    MCdf = pd.DataFrame(ModelComparison)
    
   #NAIVE METHOD
    dd= np.asarray(train[i])
    y_hat = val.copy()
    y_hat['naive'] = dd[len(dd)-1]
    naive_rms = sqrt(mean_squared_error(val[i], y_hat.naive))  
    MCdf = MCdf.append({'Model': 'Naive', 'RMSE':naive_rms, 'AIC': None}, ignore_index=True)
    
   #SIMPLE AVERAGE
    y_hat['avg_forecast'] = train[i].mean()
    simple_avg_rms = sqrt(mean_squared_error(val[i], y_hat.avg_forecast))
    MCdf = MCdf.append({'Model': 'Simple Avg', 'RMSE':simple_avg_rms, 'AIC': None}, ignore_index=True)
    
   #EXPONENTIAL SMOOTHING
    SES_model = SimpleExpSmoothing(np.asarray(train[i])).fit(smoothing_level=0.8,optimized=True)
    #SES_model = SimpleExpSmoothing(np.asarray(train[i])).fit(optimized=True)
    y_hat['SES'] = SES_model.forecast(len(val))
    SES_model_rms = sqrt(mean_squared_error(val[i], y_hat.SES))
    aic=SES_model.aic
    MCdf = MCdf.append({'Model': 'Simple Exponential Smoothing', 'RMSE':SES_model_rms, 'AIC':aic}, ignore_index=True)

   #HOLT'S LINEAR TREND METHOD
    model_HLTM = Holt(np.asarray(train[i])).fit(smoothing_level = 0.3,smoothing_slope = 0.1)
    y_hat['Holt_linear'] = model_HLTM.forecast(len(val[i]))
    model_HLTM_rms = sqrt(mean_squared_error(val[i], y_hat.Holt_linear))
    MCdf = MCdf.append({'Model': 'Holts Line', 'RMSE':model_HLTM_rms, 'AIC': model_HLTM.aic}, ignore_index=True)
    
    #HOLT-WINTERS METHOD
    model_hotwinter = ExponentialSmoothing(np.asarray(train[i]) ,seasonal_periods=7 ,trend='add', seasonal='add',).fit()
    y_hat['Holt_Winter'] = model_hotwinter.forecast(len(val[i])) 
    model_hotwinter_rms = sqrt(mean_squared_error(val[i], y_hat.Holt_Winter))
    MCdf = MCdf.append({'Model': 'Holts-Winters Line', 'RMSE':model_HLTM_rms, 'AIC': model_HLTM.aic}, ignore_index=True)
    
    MCdf = MCdf.sort_values(['RMSE'],ascending=True)
    MCdf
    BestModel = MCdf.iloc[0,0]
    print('Best Model for',i,' is ',BestModel, ' with RMSE ', round(MCdf.iloc[0,1],2))
    
   # Create directory
    
    
    dirName = os.path.join('C:\\Users\\12253\\Practicum\\Dow Forecast', i)
 
    try:
   # Create target Directory
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")
        
    fordate = ['2019-09-01', '2019-10-01', '2019-11-01', '2019-12-01',
               '2020-01-01', '2020-02-01']
    fordate = pd.to_datetime(fordate)
    
    if BestModel == 'ARIMA':
         #plot the predictions for validation set
        Model = M1_stepwise.summary()
        fileName = i + 'BMP_Arima.pdf'
        filefor = i + '_Forecast.pdf'
        fileName_xlsx = i+'Model.xlsx'
        file = os.path.join(dirName, fileName)
        filexs = os.path.join(dirName, fileName_xlsx)
        filef = os.path.join(dirName, filefor)
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,9))
        fig.suptitle('Arima Model')
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(forecast, label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(0.1, 0.001, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        
        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        
        
        #FORECAST CREATION
        M1_stepwise = pm.auto_arima(tsdow[i], start_p=1, start_q=1,
                             max_p=3, max_q=3, m=12,
                             start_P=0, seasonal=False,
                             d=1, D=1, trace=True,
                             error_action='ignore',  # don't want to know if an order does not work
                             suppress_warnings=True,  # don't want convergence warnings
                             stepwise=True)
        forecast2 = M1_stepwise.predict(n_periods=len(val[i]))
        forecast2 = pd.DataFrame(forecast2,index = fordate,columns=['Forecast'])
        Model = M1_stepwise.summary()
        
        #PLOT CREATION
        figf = plt.figure(figsize=(15,15))
        figf.suptitle('Arima Model')
        gs = figf.add_gridspec(2,2)
        ax1 = figf.add_subplot(gs[0, :])
        ax2 = figf.add_subplot(gs[1, 0])
        ax3 = figf.add_subplot(gs[1, 1])
        ax1.plot(tsdow[i], label='Demand')
        #axs[0].plot(val[i], label='Valid', color='green')
        ax1.plot(forecast2, label='Forecast', color='red')
        ax1.set(xlabel='Due Date', ylabel='Realigned History')
        ax1.legend(loc='best')
        ax2.text(.000001, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax2.axis('off')
        ax3.text(.3, .8, str(forecast2), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax3.axis('off')
        figf.savefig(filef) #best format to save picture
        
        writera = pd.ExcelWriter(filexs)
        MCdf.to_excel(writera,'Model Comparison')
        forecast2.to_excel(writera,'Forecast')
        writera.save()
        
    elif BestModel == 'Naive':
        fileName = i + 'BMP_Naive.pdf'
        fileName_xlsx = i+'Model.xlsx'
        file = os.path.join(dirName, fileName)
        filexs = os.path.join(dirName, fileName_xlsx)
        Model = pd.DataFrame(np.array(y_hat['naive']),index = y_hat.index,columns=['Forecast'])
        filefor = i + '_Forecast.pdf'
        filef = os.path.join(dirName, filefor)
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,9))
        fig.suptitle('Naive Prediction')
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(y_hat.index[:6],y_hat['naive'], label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(0.4, 0.5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')

        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        
        
        
        #FORECAST PLOT
        Model = pd.DataFrame(np.array(y_hat['naive']),index = fordate,columns=['Forecast'])
        fig2, axs = plt.subplots(2,figsize=(10,9))
        fig2.suptitle('Naive Prediction')
        axs[0].plot(tsdow[i], label='Demand')
        axs[0].plot(Model['Forecast'], label='Forecast', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(.4, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        plt.savefig(filef)
        
        writern = pd.ExcelWriter(filexs)
        MCdf.to_excel(writern,'Model Comparison')
        Model.to_excel(writern,'Forecast')
        writern.save()
        
    elif BestModel == 'Simple Avg':
        fileName = i + 'BMP_SimpleAvg.pdf'
        fileName_xlsx = i+'Model.xlsx'
        file = os.path.join(dirName, fileName)
        filexs = os.path.join(dirName, fileName_xlsx)
        Model = pd.DataFrame(np.array(y_hat['avg_forecast']),index = y_hat.index,columns=['Forecast'])
        filefor = i + '_Forecast.pdf'
        filef = os.path.join(dirName, filefor)
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,9))
        fig.suptitle('Simple Average Prediction')
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(y_hat.index[:6],y_hat['avg_forecast'], label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(0.4, 0.5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')

        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        
        
        
        #FORECAST PLOT
        Model = pd.DataFrame(np.array(y_hat['avg_forecast']),index = fordate,columns=['Forecast'])
        fig2, axs = plt.subplots(2,figsize=(10,9))
        fig2.suptitle('Simple Average Prediction')
        axs[0].plot(tsdow[i], label='Demand')
        axs[0].plot(Model['Forecast'], label='Forecast', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(.4, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        plt.savefig(filef)
        
        writersa = pd.ExcelWriter(filexs)
        MCdf.to_excel(writersa,'Model Comparison')
        Model.to_excel(writersa,'Forecast')
        writersa.save()
        
    elif BestModel == 'Simple Exponential Smoothing':
        fileName = i + 'BMP_SES.pdf'
        file = os.path.join(dirName, fileName)
        fileName_xlsx = i+'Model.xlsx'
        filefor = i + '_Forecast.pdf'
        filexs = os.path.join(dirName, fileName_xlsx)
        filef = os.path.join(dirName, filefor)
        Model = SES_model.summary()
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,9))
        fig.suptitle('Simple Exponential Smoothing Model')
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(y_hat.index[:6],y_hat['SES'], label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[0].legend(loc='best')
        axs[1].text(0.1, 0.1, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        
        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        

        #FORECAST CREATION
        SES_model = SimpleExpSmoothing(np.asarray(tsdow[i])).fit(smoothing_level=0.8,optimized=True)
        SES_forecast = SES_model.forecast(len(val))
        SES_forecast = pd.DataFrame(SES_forecast,index = fordate,columns=['Forecast'])
        Model = SES_model.summary()
        
        #PLOT CREATION
        figf = plt.figure(figsize=(15,15))
        figf.suptitle('Simple Exponential Smoothing')
        gs = figf.add_gridspec(2,2)
        ax1 = figf.add_subplot(gs[0, :])
        ax2 = figf.add_subplot(gs[1, 0])
        ax3 = figf.add_subplot(gs[1, 1])
        ax1.plot(tsdow[i], label='Demand')
        #axs[0].plot(val[i], label='Valid', color='green')
        ax1.plot(SES_forecast, label='Forecast', color='red')
        ax1.set(xlabel='Due Date', ylabel='Realigned History')
        ax1.legend(loc='best')
        ax2.text(.000001, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax2.axis('off')
        ax3.text(.3, .8, str(SES_forecast), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax3.axis('off')
        figf.savefig(filef) #best format to save picture
        
        writerses = pd.ExcelWriter(filexs)
        MCdf.to_excel(writerses,'Model Comparison')
        SES_forecast.to_excel(writerses,'Forecast')
        writerses.save()
       
    elif BestModel == 'Holts Line':
        fileName = i + 'BMP_HL.pdf'
        file = os.path.join(dirName, fileName)
        fileName_xlsx = i+'Model.xlsx'
        filexs = os.path.join(dirName, fileName_xlsx)
        filefor = i + '_Forecast.pdf'
        filef = os.path.join(dirName, filefor)
        Model = model_HLTM.summary()
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,9))
        fig.suptitle("Holt's Linear Trend Model")
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(y_hat.index[:6],y_hat['Holt_linear'], label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[1].text(0.1, 0.1, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        
        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        MCdf.to_excel(filexs,'Model Comparison') 
        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        

        #FORECAST CREATION
        model_HLTMf = Holt(np.asarray(tsdow[i])).fit(smoothing_level = 0.3,smoothing_slope = 0.1)
        model_HLTMf = model_HLTMf.forecast(len(val))
        model_HLTMf = pd.DataFrame(model_HLTMf,index = fordate,columns=['Forecast'])
        Model = model_HLTMf.summary()
        #PLOT CREATION
        figf = plt.figure(figsize=(15,15))
        figf.suptitle("Holt's Linear Trend")
        gs = figf.add_gridspec(2,2)
        ax1 = figf.add_subplot(gs[0, :])
        ax2 = figf.add_subplot(gs[1, 0])
        ax3 = figf.add_subplot(gs[1, 1])
        ax1.plot(tsdow[i], label='Demand')
        #axs[0].plot(val[i], label='Valid', color='green')
        ax1.plot(model_HLTMf, label='Forecast', color='red')
        ax1.set(xlabel='Due Date', ylabel='Realigned History')
        ax1.legend(loc='best')
        ax2.text(.000001, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax2.axis('off')
        ax3.text(.3, .8, str(model_HLTMf), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax3.axis('off')
        figf.savefig(filef) #best format to save picture
        
        writerhl = pd.ExcelWriter(filexs)
        MCdf.to_excel(writerhl,'Model Comparison')
        model_HLTMf.to_excel(writerhl,'Forecast')
        writerhl.save()
        
    elif BestModel == 'Holts-Winters Line':
        fileName = i + 'BMP_HW.pdf'
        file = os.path.join(dirName, fileName)
        fileName_xlsx = i+'Model.xlsx'
        filefor = i + '_Forecast.pdf'
        filef = os.path.join(dirName, filefor)
        Model = model_hotwinter.summary()
        filexs = os.path.join(dirName, fileName_xlsx)
        
        #PLOT CREATION
        fig, axs = plt.subplots(2,figsize=(10,12))
        fig.suptitle("Holt's-Winter's Line")
        axs[0].plot(train[i], label='Train')
        axs[0].plot(val[i], label='Valid', color='green')
        axs[0].plot(y_hat.index[:6],y_hat['Holt_Winter'], label='Prediction', color='red')
        axs[0].set(xlabel='Due Date', ylabel='Realigned History')
        axs[1].text(0.1, 0.0000001, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        axs[1].axis('off')
        
        #PLOT OUTPUT
        plt.savefig(file) #best format to save picture
        


        #FORECAST CREATION
        model_hotwinterf = ExponentialSmoothing(np.asarray(tsdow[i]) ,seasonal_periods=7 ,trend='add', seasonal='add',).fit()
        model_hotwinterf = model_hotwinterf.forecast(len(val))
        model_hotwinterf = pd.DataFrame(model_hotwinterf,index = fordate,columns=['Forecast'])
        Model = model_hotwinterf.summary()
        
        #PLOT CREATION
        figf = plt.figure(figsize=(15,20))
        figf.suptitle("Holt's Linear Trend")
        gs = figf.add_gridspec(2,2)
        ax1 = figf.add_subplot(gs[0, :])
        ax2 = figf.add_subplot(gs[1, 0])
        ax3 = figf.add_subplot(gs[1, 1])
        ax1.plot(tsdow[i], label='Demand')
        #axs[0].plot(val[i], label='Valid', color='green')
        ax1.plot(model_hotwinterf, label='Forecast', color='red')
        ax1.set(xlabel='Due Date', ylabel='Realigned History')
        ax1.legend(loc='best')
        ax2.text(.000001, .5, str(Model), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax2.axis('off')
        ax3.text(.3, .8, str(model_hotwinterf), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
        ax3.axis('off')
        figf.savefig(filef) #best format to save picture
        
        writerhw = pd.ExcelWriter(filexs)
        MCdf.to_excel(writerhw,'Model Comparison')
        model_hotwinterf.to_excel(writerhw,'Forecast')
        writerhw.save()


# In[ ]:




