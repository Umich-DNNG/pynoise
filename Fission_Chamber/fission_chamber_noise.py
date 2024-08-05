#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:48:42 2024

@author: fdarby
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.optimize import curve_fit

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

import seaborn as sns
sns.set(rc={"figure.dpi": 350, 'savefig.dpi': 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)

dwell_time = 200e-6
fs = 1/dwell_time

nperseg_num = 4096

# Data loading
data_folder = "/Users/fdarby/University of Michigan Dropbox/ENGIN-Well-counter/CROCUS/SANDCASTLE_2024_CROCUS_Campaign/Fission Chambers/08072024_54mW/"

data_folder = ""

print('loading in C1')
C1 = np.loadtxt((data_folder + "C1--SC-08072024-54mW-00000--00000.txt"),
                delimiter=',',skiprows=5)

print(C1)
print(len(C1))

print('loading in C2')
C2 = np.loadtxt((data_folder + "C2--SC-08072024-54mW-00000--00000.txt"),
                delimiter=',',skiprows=5)

print(C2)
print(len(C2))

print('loading in C3')
C3 = np.loadtxt((data_folder + "C3--SC-08072024-54mW-00000--00000.txt"),
                delimiter=',',skiprows=5)

print(C3)
print(len(C3))

print('loading in C4')
C4 = np.loadtxt((data_folder + "C4--SC-08072024-54mW-00000--00000.txt"),
                delimiter=',',skiprows=5)

print(C4)
print(len(C4))

def plot_signal_hists(C_data,leg_label):
    
    plt.plot(C_data[:,0], C_data[:,1], label=leg_label)
    plt.xlabel('Time (s)')
    plt.ylabel('Signal (V)')
    plt.legend()
    plt.show()
    
    return


# exit()

plot_signal_hists(C1,'C1')
plot_signal_hists(C2,'C2')
plot_signal_hists(C3,'C3')
plot_signal_hists(C4,'C4')

exit()
def APSD(C_data,fs,nperseg_num):
    
    f, Pxx = signal.welch(C_data[:,1],fs,nperseg=nperseg_num)
    
    return f, Pxx

f, Pxx1 = APSD(C1,fs,nperseg_num)
f, Pxx2 = APSD(C2,fs,nperseg_num)
f, Pxx3 = APSD(C3,fs,nperseg_num)
f, Pxx4 = APSD(C4,fs,nperseg_num)

def plot_PSD(f,P):

    plt.plot(f[2:-1],P[2:-1])
    plt.xscale('log')
    plt.show()

    return

# plot_PSD(f,Pxx1)
# plot_PSD(f,Pxx2)
# plot_PSD(f,Pxx3)
# plot_PSD(f,Pxx4)

def PSD_fit(f, A, alpha, c):
    return A / (1+(f**2/alpha**2)) + c

def fit_PSD(f, P):
    
    index = (
        (f < 45) | 
        ((f > 56) & (f < 148)) |
        ((f > 152) & (f < 248)) |
        ((f > 252) & (f < 300))
        )
    
    f = f[index]
    P = P[index]
    
    # plot_PSD(f,P)
    
    popt, pcov = curve_fit(PSD_fit, f[2:-1], P[2:-1],
                                     p0=[P[2], 25, 1e-6],
                                     # bounds=(0, np.inf),
                                     maxfev=int(1e6)
                                     )
    
    # print(popt)
    
    return popt, pcov

Dv = 0.8
F = 41.18e-3/3.2e-11 # 41.18 mW / 3.2e-11 J/fission = fissions/sec
rho = 0

def calc_beta_eff(A,C_data1,C_data2,Dv,F,rho):
    
    C1_bar = np.average(C_data1[:,1])
    C2_bar = np.average(C_data2[:,1])
    
    # DROP THE TWO?!
    # beta_eff = rho + np.sqrt(2*C1_bar*C2_bar*Dv/(A*F))
    beta_eff = rho + np.sqrt(C1_bar*C2_bar*Dv/(A*F))
    # beta_eff = rho + np.sqrt(2*C1_bar*C2_bar*Dv/(A*F)/np.pi)
    
    return beta_eff

def plot_and_fit_PSD(f,P,C_data1,C_data2,Dv,F,rho,leg_label):
    
    popt, pcov = fit_PSD(f, P)
    
    fig2, ax2 = plt.subplots()
    ax2.semilogx(f[2:-1], P[2:-1], '.', label=leg_label)
    ax2.semilogx(f[2:-1], PSD_fit(f[2:-1], *popt), '--', label='fit')
    ymin, ymax = ax2.get_ylim()
    dy = ymax-ymin
    # ax2.set_xlim([1, 200])
    ax2.set_xlabel('Frequency (Hz)')
    ax2.set_ylabel('PSD (V$^2$/Hz)')
    alph_str = (r'$\alpha$ = (' +
              str(np.around(popt[1]*2*np.pi, decimals=2))+
              ' +/- '+ 
              str(np.around(np.sqrt(pcov[1,1])*2*np.pi, decimals=2))
              +') 1/s')
    # ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
    #             fontsize=16, fontweight='bold',
    #             color='black', backgroundcolor='white')
    ax2.text(100, ymax-0.5*dy, alph_str)
    beta_eff = calc_beta_eff(popt[0],C_data1,C_data2,Dv,F,rho)
    beta_str = (r'$\beta_{eff}$ = ' +
              str(np.around(beta_eff, decimals=7))
              )
    # ax2.annotate(alph_str, xy=(1.5, ymin+0.1*dy), xytext=(1.5, ymin+0.1*dy),
    #             fontsize=16, fontweight='bold',
    #             color='black', backgroundcolor='white')
    ax2.text(100, ymax-0.5*dy, alph_str)
    ax2.text(100, ymax-0.6*dy, beta_str)
    
    # ax2.set_title(plt_title)
    ax2.legend(loc='upper right')
    
    plt.show()
    
    return

plot_and_fit_PSD(f,Pxx1,C1,C1,Dv,F,rho,'C1')
plot_and_fit_PSD(f,Pxx2,C2,C2,Dv,F,rho,'C2')
plot_and_fit_PSD(f,Pxx3,C3,C3,Dv,F,rho,'C3')
plot_and_fit_PSD(f,Pxx4,C4,C4,Dv,F,rho,'C4')

def CPSD(C_data1,C_data2,fs,nperseg_num):
    
    f, Pxy = signal.csd(C_data1[:,1],C_data2[:,1],fs,nperseg=nperseg_num)
    
    Pxy = np.real(Pxy)
    
    return f, Pxy

f, P12 = CPSD(C1,C2,fs,nperseg_num)
f, P13 = CPSD(C1,C3,fs,nperseg_num)
f, P14 = CPSD(C1,C4,fs,nperseg_num)
f, P23 = CPSD(C2,C3,fs,nperseg_num)
f, P24 = CPSD(C2,C4,fs,nperseg_num)
f, P34 = CPSD(C3,C4,fs,nperseg_num)

# plot_PSD(f,P12)
# plot_PSD(f,P13)
# plot_PSD(f,P14)
# plot_PSD(f,P23)
# plot_PSD(f,P24)
# plot_PSD(f,P34)

plot_and_fit_PSD(f,P12,C1,C2,Dv,F,rho,'C1/C2')
plot_and_fit_PSD(f,P13,C1,C3,Dv,F,rho,'C1/C3')
plot_and_fit_PSD(f,P14,C1,C4,Dv,F,rho,'C1/C4')
plot_and_fit_PSD(f,P23,C2,C3,Dv,F,rho,'C2/C3')
plot_and_fit_PSD(f,P24,C2,C4,Dv,F,rho,'C2/C4')
plot_and_fit_PSD(f,P34,C3,C4,Dv,F,rho,'C3/C4')