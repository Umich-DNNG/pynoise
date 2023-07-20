# This script takes in a text file of times 
# and returns a plot of the time on the y-axis and event number on the x-axis.
# Created by Jesson Hutchinson

# version history:
# v0: 08/31/2020

import os
import sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats
from matplotlib import pyplot as plt


def plot_time(time_list,fname):
    print('Reading data')
    
    xplot = []
    filedata = []
    
    #for i in range(0,len(time_list)):
    for i in range(0,100):
        filedata.append(time_list[i]*1e-9)
        xplot.append(i)
    
    num_lines=len(time_list)
    
    print('# lines in file = ',num_lines)
    
    xplot = tuple(xplot)
    filedata = tuple(filedata)
    
    xlin = np.linspace(0,num_lines-1,100)
    ylin = np.linspace(0,max(filedata),100)

    data_fit = np.polyfit(xplot, filedata, 1)
    predict = np.poly1d(data_fit)
    data_fit_plot = predict(xlin)
    
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(xplot, filedata)
    print('slope = ',slope,'int =',intercept,'r^2 = ',r_value,'p_value = ',p_value,'std err = ',std_err)
    
    plt.plot(xplot,filedata,label='Data')
    plt.plot(xlin,data_fit_plot,label='Linear')
    plt.xlabel('Event number')
    plt.ylabel('Time (sec)')
    plt.text(80,0,r'$R^2$ = '+str(round(r_value,3)))
    plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    plt.legend()
    plt.savefig(fname+'_TimeVsEvents.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
    plt.savefig(fname+'_TimeVsEvents.eps',dpi=500,bbox_inches='tight',pad_inches=0.1)
    #plt.show
    plt.close()
    
    print('finished')

# #fname = sys.argv[1]    
# fname = 'C15short.txt'
# plot_out_file_ext = '.jpg'
# plot_time = plot_time(fname)
