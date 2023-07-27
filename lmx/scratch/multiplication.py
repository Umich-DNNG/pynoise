# Performs a multiplicity analysis
# Equations are from 2018 ANE paper

# v000: 12/17/2022: initial version tracking

# standard imports
import math

# Test data from SCRaP file '2016_12_01_170022_0-Sequential.csv', inside file 'C00 summary.xlsx'
#nuI1 = 3.182
#dnuI1 = 0.010
#nuI2 = 4.098
#dnuI2 = 0.011
#nuS1 = 2.154
#dnuS1 = 0.005
#nuS2 = 1.894
#dnuS2 = 0.015
#R1 = 19065.8828125
#dR1 = 4.03205242657195
#R2 = 6979.00
#dR2 = 19.3340884603104
#dR1R2 = 68.8350431446098
#eff = 0.0221069760032387
#deff = 0.000221090568520993
#alpha = 0.033
#beta_eff = 0.00202


def calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_list, eff):
    
    Ml_list = []
    a1_list = []
    a2_list = []
    a3_list = []
    a4_list = []
    
    a1 = nuS1*nuI2/(nuI1-1)
    a2 = nuS2 - a1
    
    for i in range(0,len(gatewidth_list)):
        # Eq 52
        a3 = -R2_list[i]*nuS1/(R1_list[i]*eff)
        if (a2**2-4*a1*a3) > 0:
            a4 = math.sqrt(a2**2-4*a1*a3)
        else:
            a4 = 1e-10
        Ml = (-a2+a4)/(2*a1)
    
        Ml_list.append(Ml)
        a1_list.append(a1)
        a2_list.append(a2)
        a3_list.append(a3)
        a4_list.append(a4)
    
    return Ml_list, a1_list, a2_list, a3_list, a4_list

def calc_dMl(gatewidth_list, a3_list, a4_list, R1_list, dR1_list, R2_list, dR2_list, dR1R2_list, eff, deff):
    
    dMl_list = []
    dMldR1_list = []
    dMldR2_list = []
    dMldeff_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq 55
        dMldR1 = a3_list[i]/(R1_list[i]*a4_list[i])
        dMldR2 = -a3_list[i]/(R2_list[i]*a4_list[i])
        dMldeff = a3_list[i]/(eff*a4_list[i])
        dMl = math.sqrt(dMldR1**2*dR1_list[i]**2 + dMldR2**2*dR2_list[i]**2 + 2*dMldR1*dMldR2*dR1R2_list[i] + dMldeff**2*deff**2)
    
        dMl_list.append(dMl)
        dMldR1_list.append(dMldR1)
        dMldR2_list.append(dMldR2)
        dMldeff_list.append(dMldeff)
        
    return dMl_list, dMldR1_list, dMldR2_list, dMldeff_list

def calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_list, eff):
    
    Fs_list = []
    a5_list = []
    a6_list = []
    a7_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq 57
        a5 = -(R1_list[i]**2*(nuI2*nuS1+nuS2-nuI1*nuS2))/((nuI1-1)*nuS1**2)
        a6 = (nuI2*R1_list[i]**3)/((nuI1-1)*nuS1**2*eff)
        if (a5**2+4*R2_list[i]*a6) > 0:
            a7 = math.sqrt(a5**2+4*R2_list[i]*a6)
        else:
            a7 = 1e-10
        Fs = (a5+a7)/(2*R2_list[i])
        
        Fs_list.append(Fs)
        a5_list.append(a5)
        a6_list.append(a6)
        a7_list.append(a7)
        
    return Fs_list, a5_list, a6_list, a7_list

def calc_dFs(gatewidth_list, a5_list, a6_list, a7_list, R1_list, dR1_list, R2_list, dR2_list, dR1R2_list, eff, deff):
    
    dFs_list = []
    dFsdR1_list = []
    dFsdR2_list = []
    dFsdeff_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq 58
        dFsdR1 = (a5_list[i]*a7_list[i]+a5_list[i]**2+3*a6_list[i]*R2_list[i])/(R1_list[i]*R2_list[i]*a7_list[i])
        dFsdR2 = (a6_list[i]/(R2_list[i]*a7_list[i]))-((a5_list[i]+a7_list[i])/(2*R2_list[i]**2))
        dFsdeff = -a6_list[i]/(eff*a7_list[i])
        dFs = math.sqrt(dFsdR1**2*dR1_list[i]**2 + dFsdR2**2*dR2_list[i]**2 + 2*dFsdR1*dFsdR2*dR1R2_list[i] + dFsdeff**2*deff**2)
        
        dFs_list.append(dFs)
        dFsdR1_list.append(dFsdR1)
        dFsdR2_list.append(dFsdR2)
        dFsdeff_list.append(dFsdeff)

    return dFs_list, dFsdR1_list, dFsdR2_list, dFsdeff_list

def calc_Mt(gatewidth_list, Ml_list, nuI1, alpha):
    
    Mt_list = []
    
    for i in range(0,len(gatewidth_list)):   
        # Eq H3 in SCRaP benchmark
        Mt = (Ml_list[i]*nuI1-1-alpha)/(nuI1-1-alpha)
        
        Mt_list.append(Mt)
    
    return Mt_list

def calc_dMt(gatewidth_list, nuI1, alpha, dMl_list):
    
    dMt_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq H4 in SCRaP benchmark
        dMt = (nuI1/(nuI1-1-alpha))*dMl_list[i]
        
        dMt_list.append(dMt)
    
    return dMt_list

def calc_kp(gatewidth_list, Mt_list):
    
    kp_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq H5 of SCRaP
        kp = 1-1/Mt_list[i]
        
        kp_list.append(kp)
    
    return kp_list

def calc_dkp(gatewidth_list, Mt_list, dMt_list):
    
    dkp_list = []
    
    for i in range(0,len(gatewidth_list)):  
        # Eq H6 of SCRaP
        dkp = dMt_list[i]/Mt_list[i]**2
    
        dkp_list.append(dkp)
    
    return dkp_list

def calc_keff(gatewidth_list, kp_list, beta_eff):
    
    keff_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq H7 of SCRaP
        keff = kp_list[i]/(1-beta_eff)
        
        keff_list.append(keff)
        
    return keff_list
    
def calc_dkeff(gatewidth_list, dkp_list, beta_eff):
    
    dkeff_list = []
    
    for i in range(0,len(gatewidth_list)):
        # Eq H8 of SCRaP
        dkeff = dkp_list[i]/(1-beta_eff)
        
        dkeff_list.append(dkeff)
    
    return dkeff_list









## testing
#Ml, a1, a2, a3, a4 = calc_Ml(nuS1, nuS2, nuI1, nuI2, R1, R2, eff)
#Fs, a5, a6, a7 = calc_Fs(nuS1, nuS2, nuI1, nuI2, R1, R2, eff)
#dMl, dMldR1, dMldR2, dMldeff = calc_dMl(a3, a4, R1, dR1, R2, dR2, dR1R2, eff, deff)
#dFs, dFsdR1, dFsdR2, dFsdeff = calc_dFs(a5, a6, a7, R1, dR1, R2, dR2, dR1R2, eff, deff)
#Mt = calc_Mt(Ml, nuI1, alpha)
#dMt = calc_dMt(nuI1, alpha, dMl)
#kp = calc_kp(Mt)
#dkp = calc_dkp(Mt, dMt)
#keff = calc_keff(kp, beta_eff)
#dkeff = calc_dkeff(dkp, beta_eff)
#print('Ml ',Ml,' +/- ',dMl)
#print('Mt ',Mt,' +/- ',dMt)
#print('Fs ',Fs,' +/- ',dFs)
#print('kp ',kp,' +/- ',dkp)
#print('keff ',keff,' +/- ',dkeff)
#print(dFsdR1,dFsdR2,dFsdeff)
