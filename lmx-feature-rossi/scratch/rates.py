# Performs rate calculations
# All take in lists and output lists
# Equations are from 2018 ANE paper


# standard imports
import os
import numpy as np
import sys
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter


def omega2_single(B,gatewidths):
    
    """ Calculates omega2 using Equation 32.
    B is a value and gatewidths is a list.
    Returns a list of omega2 results with length equal to the number of gatewidths provided"""
    
    omega2_single = []
    
    for gatewidth in gatewidths:
        omega2_single.append(1-((1-np.exp(-gatewidth*B))/(gatewidth*B)))
    
    return omega2_single


def omega2_double(Aper,B,Cper,D,gatewidths):
    
    """ Calculates omega2 using (Aper * (1 - (1 - np.exp(-B * gatewidth)) / (B* gatewidth)))+(Cper * (1 - (1 - np.exp(-D * gatewidth)) / (D* gatewidth).
    A-D are values and gatewidths is a list.
    Returns a list of omega2 results with length equal to the number of gatewidths provided"""
    
    omega2_double = []
    
    for gatewidth in gatewidths:
        omega2_double.append(Aper*(1-((1-np.exp(-gatewidth*B))/(gatewidth*B)))+Cper*(1-((1-np.exp(-gatewidth*D))/(gatewidth*D))))
    
    return omega2_double


def R2_calc_rate(Y2,omega2):
    
    """ Calculates R2 using Equation 35.
    Y2 and omega 2 are lists of the same length.
    Returns a list of R2 results with length equal to the length of Y2 and omega2."""
    
    R2_rate = []
    
    if len(Y2) != len(omega2):
        sys.exit('Exit: Y2 and omega2 must have the same length.')
    
    for i in range(0,len(Y2)):
        # Equation 35
        R2_rate.append(Y2[i]/omega2[i])
    
    return R2_rate


def R2_unc_calc(gatewidths,R2, omega2, dY2, B, dB):
    
    """ Calculates R2 unc using Eq 36.
    Gatewidths, R2, omega2, and dY2 are lists of the same length.
    B and dB are values (B is the same as lambda in the paper).
    Returns a list of R2 unc results with length equal to gatewidths, R2, omega2, and dY2."""
    
    R2_rate_unc = []
    
    if len(R2) != len(gatewidths):
        sys.exit('Exit: R2 and gatewidths must have the same length.')
    if len(R2) != len(omega2):
        sys.exit('Exit: R2 and omega2 must have the same length.')
    if len(R2) != len(dY2):
        sys.exit('Exit: R2 and Y2 unc must have the same length.')

    for i in range(0,len(R2)):
        # Equation 36
        # Note that the units for R2 and B don't match. This doesn't matter, however, as one would multiply and divide by the same constant.
        R2_rate_unc.append(np.sqrt((dY2[i]**2 + R2[i]**2*(1-omega2[i]-np.exp(-B*gatewidths[i]))**2*dB**2/B**2)/omega2[i]**2))
        
    return R2_rate_unc


def R2_double_unc_calc(gatewidths,R2, omega2, dY2, Aper, B, dB, Cper, D, dD, dBD):
    
    """ Calculates R2 unc when using omega2 with 2 terms.
    Gatewidths, R2, omega2, and dY2 are lists of the same length.
    Aper, B, dB, Cper, D, dD are values (B is the same as lambda1, D is the same as lambda2).
    Returns a list of R2 unc results with length equal to gatewidths, R2, omega2, and dY2.
    See equations in EUCLID subcritical paper."""
    
    R2_rate_unc = []
    
    if len(R2) != len(gatewidths):
        sys.exit('Exit: R2 and gatewidths must have the same length.')
    if len(R2) != len(omega2):
        sys.exit('Exit: R2 and omega2 must have the same length.')
    if len(R2) != len(dY2):
        sys.exit('Exit: R2 and Y2 unc must have the same length.')

    for i in range(0,len(R2)):
        # See equations in EUCLID subcritical paper
        dR2dY2 = 1/omega2[i]
        dR2dB = (R2[i]*Aper*((np.exp(-B*gatewidths[i])*(1+B*gatewidths[i]))-1))/(omega2[i]*B**2*gatewidths[i])
        dR2dD = (R2[i]*Cper*((np.exp(-D*gatewidths[i])*(1+D*gatewidths[i]))-1))/(omega2[i]*D**2*gatewidths[i])
        R2_rate_unc.append((dR2dY2**2*dY2[i]**2+dR2dB**2*dB**2+dR2dD**2*dD**2+2*dR2dB*dR2dD*dBD)**0.5)
        
    return R2_rate_unc


def reduced_factorial_moments(feynman_data):
    
    """ Calculates reduced factorial moments using Equations 3-6. """
    
    first_reduced_factorial_moment_list = []
    second_reduced_factorial_moment_list = []
    third_reduced_factorial_moment_list = []
    fourth_reduced_factorial_moment_list = []
    n_list = []
    
    for current_histogram in feynman_data:
        
        n = [i for i in range(0,len(current_histogram))]
        
        sum_Cn = sum(current_histogram)
        
        m1_products = []
        for i in range(0, len(current_histogram)):
            m1_products.append(n[i] * current_histogram[i])
        # Equation 3
        m1 = sum(m1_products)/sum_Cn
        
        m2_products = []
        for i in range(1, len(current_histogram)):
            m2_products.append(n[i] * n[i-1] * current_histogram[i])
        # Equation 4
        m2 = sum(m2_products)/(2*sum_Cn)
        
        m3_products = []
        for i in range(2, len(current_histogram)):
            m3_products.append(n[i] * n[i-1] * n[i-2] * current_histogram[i])
        # Equation 5
        m3 = sum(m3_products)/(6*sum_Cn)
        
        m4_products = []
        for i in range(3, len(current_histogram)):
            m4_products.append(n[i] * n[i-1] * n[i-2] * n[i-3] * current_histogram[i])
        # Equation 6
        m4 = sum(m4_products)/(24*sum_Cn)
        
        first_reduced_factorial_moment_list.append(m1)
        second_reduced_factorial_moment_list.append(m2)
        third_reduced_factorial_moment_list.append(m3)
        fourth_reduced_factorial_moment_list.append(m4)
        n_list.append(n)
        
    return first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, n_list


def factorial_moments(feynman_data):
    
    """ Calculates reduced factorial moments using Equations 7-11. """
    
    first_factorial_moment_list = []
    second_factorial_moment_list = []
    third_factorial_moment_list = []
    fourth_factorial_moment_list = []
    
    for current_histogram in feynman_data:
        
        n = [i for i in range(0,len(current_histogram))]
        
        sum_Cn = sum(current_histogram)
        
        C1_products = []
        for i in range(0, len(current_histogram)):
            C1_products.append(n[i] * current_histogram[i])
        # Equation 8
        C1 = sum(C1_products)/sum_Cn
        
        C2_products = []
        for i in range(0, len(current_histogram)):
            C2_products.append(n[i] * n[i] * current_histogram[i])
        # Equation 9
        C2 = sum(C2_products)/sum_Cn
        
        C3_products = []
        for i in range(0, len(current_histogram)):
            C3_products.append(n[i] * n[i] * n[i] * current_histogram[i])
        # Equation 10
        C3 = sum(C3_products)/sum_Cn
        
        C4_products = []
        for i in range(0, len(current_histogram)):
            C4_products.append(n[i] * n[i] * n[i] * n[i] * current_histogram[i])
        # Equation 11
        C4 = sum(C4_products)/sum_Cn
        
        first_factorial_moment_list.append(C1)
        second_factorial_moment_list.append(C2)
        third_factorial_moment_list.append(C3)
        fourth_factorial_moment_list.append(C4)
        
    return first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list


def feynman_histogram_v2m(single_feynman_mean_list,single_feynman_variance_list):
    
    """ Gives mean, variance, variance-to-mean of a feynman histogram."""
    
    single_variance_to_mean_list = []
    
    for i in range(0,len(single_feynman_mean_list)):
        
        single_variance_to_mean_list.append((single_feynman_variance_list[i] - single_feynman_mean_list[i] * single_feynman_mean_list[i]) / single_feynman_mean_list[i] - 1.0)
        
    return single_variance_to_mean_list


def excess_variance_reduced(gatewidth_list, feynman_data, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list):
    
    """ Gives Y1, Y2, and their uncertainties."""

    Y1 = []
    dY1 = []
    Y2 = []
    dY2 = [] 
    
    for i in range(0,len(gatewidth_list)):
        
        N = sum(feynman_data[i])
        
        # Equation 21
        Y1.append(first_reduced_factorial_moment_list[i]/gatewidth_list[i])
        # Equation 22
        Y2.append((second_reduced_factorial_moment_list[i]-0.5*first_reduced_factorial_moment_list[i]**2)/gatewidth_list[i])
        # Equation 24
        if (2*second_reduced_factorial_moment_list[i]+first_reduced_factorial_moment_list[i]-first_reduced_factorial_moment_list[i]**2) > 0:
            dY1.append(((2*second_reduced_factorial_moment_list[i]+first_reduced_factorial_moment_list[i]-first_reduced_factorial_moment_list[i]**2)/(N-1))**0.5/gatewidth_list[i])
        else:
            dY1.append(0)
        # Equation 29
        if (6*fourth_reduced_factorial_moment_list[i]+-6*third_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]+6*third_reduced_factorial_moment_list[i]-second_reduced_factorial_moment_list[i]**2+4*second_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]**2-4*second_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]+second_reduced_factorial_moment_list[i]-first_reduced_factorial_moment_list[i]**4+first_reduced_factorial_moment_list[i]**3) > 0:
            dY2.append(((6*fourth_reduced_factorial_moment_list[i]+-6*third_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]+6*third_reduced_factorial_moment_list[i]-second_reduced_factorial_moment_list[i]**2+4*second_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]**2-4*second_reduced_factorial_moment_list[i]*first_reduced_factorial_moment_list[i]+second_reduced_factorial_moment_list[i]-first_reduced_factorial_moment_list[i]**4+first_reduced_factorial_moment_list[i]**3)/(N-1))**0.5/gatewidth_list[i])
        else:
            dY2.append(0)
    
    return Y1, dY1, Y2, dY2


def excess_variance(gatewidth_list, feynman_data, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list):
    
    """ Gives Ym and uncertainty."""

    Ym = []
    dYm = []
        
    for i in range(0,len(gatewidth_list)):
        
        N = sum(feynman_data[i])
        
        # Equation 18
        Ym.append(((second_factorial_moment_list[i]-first_factorial_moment_list[i]**2)/first_factorial_moment_list[i])-1)
        # Equation 60 of LA-UR-15-21365
        inside_numerator = (2*second_factorial_moment_list[i]**2/first_factorial_moment_list[i]**2)+(second_factorial_moment_list[i]**3/first_factorial_moment_list[i]**4)+second_factorial_moment_list[i]-first_factorial_moment_list[i]**2+(fourth_factorial_moment_list[i]/first_factorial_moment_list[i]**2)-(2*second_factorial_moment_list[i]*third_factorial_moment_list[i])/first_factorial_moment_list[i]**3-2*third_factorial_moment_list[i]/first_factorial_moment_list[i]
        if inside_numerator > 0:
            dYm.append((inside_numerator/(N-1))**0.5)
        else:
            dYm.append(0)
            print('Note: dYm was requiring a negative square root. dYm has been set to 0 (but it is not correct).')
    
    return Ym, dYm


def log_one(tau, a, b):
    """Callable equation for a single log feynman fit
       a * (1 - (1 - np.exp(-b * tau)) / (b * tau))

        Arguments:
            tau: Gatewidths
            a: Fitting Parameter (representative of plateau value)
            b: Fitting Parameter (representative of lambda value)

    Returns: Distribution for equation for the given parameters
    """
    return a * (1 - ((1 - np.exp(-b * tau)) / (b * tau)))


def log_two(tau, a, b, c, d):
    """Callable equation for a single log feynman fit
       a * (1 - ((1 - np.exp(-b * tau)) / (b * tau))) + c * (1 - ((1 - np.exp(-d * tau)) / (d * tau)))

    Arguments:
        tau: Gatewidths
        a: Fitting Parameter (representative of first plateau value)
        b: Fitting Parameter (representative of lambda 1 value)
        c: Fitting Parameter (representative of second plateau value)
        d: Fitting Parameter (representative of lambda 2 value)

    Returns: Distribution for equation for the given parameters
    """
    return a * (1 - ((1 - np.exp(-b * tau)) / (b * tau))) + c * (1 - ((1 - np.exp(-d * tau)) / (d * tau)))


def fit1Log_xml(gatewidth_list, Y2_distribution_value, Y2_distribution_unc, guess=None):
    """Calculates the curve fit for a single log Feynman fit
        
        Arguments:
            guess: Optional list of initial guess for fit parameters A, B
                    
        Returns:
            singleFitParameters: list of 2 fit parameters
            singleFitCovariance: list of lists making the 2*2 covariance matrix
    """
    
    if not guess:
        dY2s = savgol_filter(np.gradient(Y2_distribution_value, gatewidth_list), 2 * (len(gatewidth_list) // 2) - 1, 3)
        dY2s_max = np.argmax(dY2s)
        guess = [Y2_distribution_value[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max]]
    else:
        if len(guess) != 2:
            print("Initial values must be a list of two values")

    try:
        singleFitParameters, singleFitCovariance = curve_fit(log_one, gatewidth_list, Y2_distribution_value,
                                                                       guess, method="lm")
        return singleFitParameters, singleFitCovariance
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        print("More appropriate guess values may be needed")


def fit2Log_xml(gatewidth_list, Y2_distribution_value, Y2_distribution_unc, guess=None):
    """Calculates the curve fit for a double log Feynman fit
            
        Arguments:
            guess: Optional list of initial guess for fit parameters A, B
        
        Returns:
            doubleFitParameters: list of 4 fit parameters
            singleFitCovariance: list of lists making the 4x4 covariance matrix
    """
    if not guess:
        dY2s = savgol_filter(np.gradient(Y2_distribution_value, gatewidth_list), 2 * (len(gatewidth_list) // 2) - 1, 3)
        dY2s_max = np.argmax(dY2s)
        guess = [Y2_distribution_value[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max] / 2,
                 Y2_distribution_value[np.argmin(dY2s[dY2s_max:])], dY2s[dY2s_max] / 2]
    else:
        if len(guess) != 4:
            print("Initial values must be a list of four values")

    try:
        doubleFitParameters, doubleFitCovariance = curve_fit(log_two, gatewidth_list, Y2_distribution_value,
                                                                       guess, method="lm")
        return doubleFitParameters, doubleFitCovariance
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
        print("More appropriate guess values may be needed")


def total_events(gatewidth_list,histogram_x_list,histogram_y_list):
    
    for i in range(0,len(histogram_x_list)):
        
        gatewidth = gatewidth_list[i]
        current_x = histogram_x_list[i]
        current_y = histogram_y_list[i]
        
        total_gates = sum(current_y)
        
        total_events = 0
        for j in range(0,len(current_x)):
            total_events += current_x[j]*current_y[j]
        
        print('For gate-width ',gatewidth,', total_gates = ',total_gates,', and total events = ',total_events)
        
def eff_from_Cf(gatewidth_list, Y1_list, dY1_list, nuS1_Cf252, Cf252_Fs, Cf252_dFs):
    
    calc_eff_kn_list = []
    calc_eff_unc_kn_list = []
    
    for i in range(0,len(gatewidth_list)):
        Y1 = Y1_list[i]
        dY1 = dY1_list[i]
        eff = Y1/(nuS1_Cf252*Cf252_Fs)
        calc_eff_kn_list.append(eff)
        # ANE2018 Eq 50
        deff = eff*np.sqrt((dY1/Y1)**2+(Cf252_dFs/Cf252_Fs)**2)
        calc_eff_unc_kn_list.append(deff)

    return calc_eff_kn_list, calc_eff_unc_kn_list



## test for R2 unc
#Aper = 1
#Cper = 0
#B = 25000
#D = 10000
#gatewidths=[0.000256]
#Y2 = [7000]
#dY2 = [26.6]
#dB = 50
#dD = 25
#dBD = 5
#omega2 = omega2_double(Aper,B,Cper,D,gatewidths)
#R2 = R2_calc_rate(Y2,omega2)
#print(R2_unc_calc(gatewidths,R2, omega2, dY2, B, dB))
#print(R2_double_unc_calc(gatewidths,R2, omega2, dY2, Aper, B, dB, Cper, D, dD, dBD))