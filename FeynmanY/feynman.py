import numpy as np
import Event as evt
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

import seaborn as sns
sns.set(rc={"figure.dpi": 350, 'savefig.dpi': 350})
sns.set_style("ticks")
sns.set_context("talk", font_scale=0.8)


# ------------ FeynmanY Fitting Function ----------------------------------------------
def YFit(tau, gamma, alpha):
    return gamma*(1+(1-np.exp(alpha*tau))/(alpha*tau))
# -------------------------------------------------------------------------------------


class FeynmanY:
    def __init__(self, 
                 tau_range: list[int] = [30, 3000], 
                 increment_amount: int = 30, 
                 plots_scale: str = "log"):

        '''
        Description:
            - Creating a FeynmanY() object and its variables.

        Inputs:
            - tau_range (range of tau values)
            - increment_amount (the increment interval of tau)
            - plots_scale (scale of the figures)

        Outputs: 
            -Creating a FeynmanY() object
        '''

        # Required Parameters
        self.tau_range = tau_range
        self.increment_amount = increment_amount
        self.plots_scale = plots_scale
        self.gamma = None
        self.alpha = None
        self.pred = None
        self.m1 = {}
        self.m2 = {}
        self.m3 = {}
        self.m4 = {}
        self.m5 = {}
        self.m6 = {}
        self.omega1 = {}
        self.omega2 = {}
        self.omega3 = {}



    def randomCounts(self, triggers: list[evt.Event], tau: int, meas_time: float = -1):

        '''Converts a list of Events into random trigger gate frequencies.
        
        Requires:
        - triggers: the list of Events. Assumes the 
        list is sorted from least to greatest time.
        - tau: the gate width.'''

        # Convert the list of times into gate indices.
        if meas_time == -1:
            meas_time = triggers[-1]
        num_gates = int(meas_time/tau)
        frequencies = []
        count = 1
        prev = int(triggers[0].time/tau)
        # For all measurements:
        for measurement in triggers[1:]:
            cur = int(measurement.time/tau)
            # If still in the same gate, increment the count.
            if cur == prev:
                count += 1
            else:
                # If count index doesn't currently 
                # exist, append zeros until it does.
                while count > len(frequencies)-1:
                    frequencies.append(0)
                # Increase the frequency for the count index.
                frequencies[count] += 1
                # Reset variables.
                count = 1
                prev = int(measurement.time/tau)
        if count != 1:
            while count > len(frequencies)-1:
                frequencies.append(0)
            frequencies[count] += 1    
        frequencies[0] += num_gates - sum(frequencies)
        frequencies = [freq/num_gates for freq in frequencies]
        # Return probability list.
        return frequencies


    def FeynmanY_histogram(self,
                           probabilities, 
                           show_plot: bool = False,  
                           save_fig: bool = False, 
                           save_dir: str = './',
                           hvs: dict = None):

        '''Creates a histogram from a numpy array of random trigger probabilities.
        
        Requires:
        - triggers: the list of Events. Assumes the 
        list is sorted from least to greatest time.
        - tau: the gate width.'''

        bins = np.arange(len(probabilities))
        values = probabilities

        # Plot histogram using plt.bar
        plt.bar(bins, values, align='center', width=0.8,**hvs)
        plt.yscale(self.plots_scale)
        # Customize plot if needed
        plt.xlabel('r')
        plt.ylabel('$P_n^*$')
        plt.title('FeynmanY Random Trigger')

        # Saving the figure (optional)
        if save_fig:
            save_filename = os.path.join(save_dir, 'FeynmanY.png') 
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
            
        # Displaying the plot (optional)
        if show_plot:
            plt.show()

        plt.close('all')


    def computeMoments(self, probabilities: list, tau: int):

        '''Creates the two moments from probabilities.
        
        Requires:
        - probabilities (numpy array): index representing the bin count, and value representing frequency
        '''

        moment1, moment2, moment3, moment4, moment5, moment6 = 0, 0, 0, 0, 0, 0
        for i in range(len(probabilities)):
            moment1 += (i)*probabilities[i]
            moment2 += (i)*(i-1)*probabilities[i]
            moment3 += (i)*(i-1)*(i-2)*probabilities[i]
            moment4 += (i)*(i-1)*(i-2)*(i-3)*probabilities[i]
            moment5 += (i)*(i-1)*(i-2)*(i-3)*(i-4)*probabilities[i]
            moment6 += (i)*(i-1)*(i-2)*(i-3)*(i-4)*(i-5)*probabilities[i]
        moment2 /= 2
        moment3 /= 6
        moment4 /= 24
        moment5 /= 120
        moment6 /= 720
        self.m1[tau] = moment1
        self.m2[tau] = moment2
        self.m3[tau] = moment3
        self.m4[tau] = moment4
        self.m5[tau] = moment5
        self.m6[tau] = moment6
        
        return [moment1,moment2,moment3,moment4]
        
    def computeOmegas(self, lam, tau: int):
        self.omega1[tau] = 1
        self.omega2[tau] = 1 - 1/(lam*tau) * (1-np.exp(-lam*tau))
        self.omega3[tau] = 1 - 1/(2*lam*tau) * (3 - 4*np.exp(-lam*tau) + np.exp(-2*lam*tau))
    
    def computeYY2Y3(self, tau: int):
        # If moments 1 or 2 are not defined for this tau, throw an error.
        if self.m1.get(tau) is None or self.m2.get(tau) is None:
            raise ValueError()
        # Otherwise, return Y and Y2.
        return ((2*self.m2[tau] + self.m1[tau] - self.m1[tau]*self.m1[tau])/self.m1[tau] - 1, 
                (self.m2[tau] - self.m1[tau]*self.m1[tau]/2)/(tau*1e-9), 
                (self.m3[tau] - self.m2[tau]*self.m1[tau] + self.m1[tau]*self.m1[tau]*self.m1[tau]/3)/(tau*1e-9)) 
    
    def computeRR2R3(self,Y,Y2,Y3,tau):
        return (Y/self.omega1[tau],
                Y2/self.omega2[tau],
                Y3/self.omega3[tau])
    
    def computeUncR(self,Y2,Y3,meas_time,tau):
        N = int(meas_time/tau)
        # uncY2 = 0
        uncY2 = np.sqrt(6*self.m4[tau] + 6*self.m3[tau] + self.m2[tau] - self.m2[tau]**2 + 4*(self.m2[tau]*self.m1[tau])**2 + self.m1[tau]**3 - self.m1[tau]**4 - 
                6*self.m3[tau]*self.m1[tau] - 4*self.m2[tau]*self.m1[tau]) / (np.sqrt(N-1)*tau)
        uncY3 = np.sqrt( 20*self.m6[tau] + 30*self.m5[tau] + 12*self.m4[tau] + self.m3[tau] - self.m3[tau]**2 + 2*self.m2[tau]**3 + self.m1[tau]**5 - 
                self.m1[tau]**6 - 20*self.m5[tau]*self.m1[tau] - 8*self.m4[tau]*self.m2[tau] - 24*self.m4[tau]*self.m1[tau] + 14*(self.m4[tau]*self.m1[tau])**2 - 
                6*self.m3[tau]*self.m2[tau] - 6*self.m3[tau]*self.m1[tau] + 12*(self.m3[tau]*self.m1[tau])**2 - 8*(self.m3[tau]*self.m1[tau])**3 + 
                5*(self.m2[tau])**2*self.m1[tau] + self.m2[tau]*self.m1[tau]**2 - 6*(self.m2[tau]*self.m1[tau])**3 + 6*(self.m2[tau]*self.m1[tau])**4 -
                8*(self.m2[tau]**2)*(self.m1[tau]**2)+10*self.m3[tau]*self.m2[tau]*self.m1[tau]) / ( np.sqrt(N-1)*tau ) 
        return (10**9*uncY2/self.omega2[tau], 10**9*uncY3/self.omega3[tau])
    
    def plot(self, taus, ys, Ylabel, error, save_fig: bool = False, show_plot: bool = False, save_dir: str = './'):
    
        plt.plot(taus,ys)
        #if len(error) != 0:
            #plt.fill_between(taus,ys-error,ys+error)
        plt.xlabel("Gate Width (ns)")
        plt.ylabel(str(Ylabel))
        plt.ylim(0,None)
        

        # Saving the figure (optional)
        if save_fig:
            save_filename = os.path.join(save_dir, Ylabel + '_FeynmanY.png') 
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
            save_filename = os.path.join(save_dir, Ylabel + '_FeynmanY.txt')
            savedata = np.vstack((taus,ys))
            np.savetxt(save_filename,savedata)
            
        # Displaying the plot (optional)
        if show_plot:
            plt.show()
            
    def plot_moments(self, taus, moments, Ylabel, error, save_fig: bool = False, show_plot: bool = False, save_dir: str = './'):
    
        plt.plot(taus,moments[:,0],label = 'm1')
        plt.plot(taus,moments[:,1],label = 'm2')
       
        plt.xlabel("Gate Width (ns)")
        plt.yscale("log")
        plt.legend(['m1','m2'])
        plt.ylabel(str(Ylabel))
        plt.ylim(0,None)
        

        # Saving the figure (optional)
        if save_fig:
            save_filename = os.path.join(save_dir, Ylabel + '_FeynmanY.png') 
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
            
        # Displaying the plot (optional)
        if show_plot:
            plt.show()



    def fitting(self, 
                x_data, 
                y_data, 
                gamma_guess, 
                alpha_guess, 
                save_fig: bool = False, 
                show_plot: bool = False, 
                save_dir: str = './', 
                fit_opt: dict = {},
                scatter_opt: dict = {}, 
                type: str = 'Y'):

        # Convert the lists to NumPy arrays
        x = np.array(x_data)
        y = np.array(y_data)

        # Define the initial guesses as a tuple
        initial_guesses = (gamma_guess, alpha_guess)

        # Perform the curve fitting using curve_fit
        popt, pcov = curve_fit(YFit, x, y, p0=initial_guesses)
        # popt, pcov = curve_fit(YFit, x, y, p0=initial_guesses)

        # Retrieve the optimized parameters
        self.gamma, self.alpha = popt

        # Display the optimized parameters
        print("Optimized gamma:", self.gamma)
        print("Optimized alpha:", self.alpha)

        # Generate x values for plotting the fitted curve
        x_fit = np.linspace(min(x), max(x), self.increment_amount)

        # Generate y values using the fitted parameters
        self.pred = YFit(x_fit, self.gamma, self.alpha)

        # Compute residuals
        residuals = ((YFit(x, self.gamma, self.alpha) - y) / y) * 100

        # Create figure and axes
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=(8, 6), gridspec_kw={'height_ratios': [2, 1]})

        # Plotting original data points and fitted curve in top subplot
        ax1.scatter(x, y, **scatter_opt)
        ax1.plot(x_fit, self.pred, **fit_opt)
        ax1.set_ylabel(type + ' Value')
        ax1.set_title(type + ' Distribution')

        # Computing residuals and plot in bottom subplot
        # residuals_norm = residuals / np.max(np.abs(residuals))

        ax2.scatter(x, residuals, **scatter_opt)
        ax2.axhline(y=0, color='#162F65', linestyle='--')
        # ax2.set_ylim([-1, 1])
        ax2.set_xlabel('Tau Values')
        ax2.set_ylabel('Percent difference (%)')

        prev_label = fit_opt.get('label')
        fit_opt['label'] = (prev_label if prev_label != None else 'Fitted Curve') + f' (gamma={self.gamma:.3g}, alpha={self.alpha:.3g})'
        
        # Plot the original data points and the fitted curve
        # plt.scatter(x, y, **scatter_opt)
        # plt.plot(x_fit, self.pred, **fit_opt)
        # plt.xlabel('Tau Value')
        # plt.ylabel(type + ' Value')
        # plt.title(type + ' Distribution')
        # plt.legend()

        if prev_label == None:
            fit_opt.pop('label')
        else:
            fit_opt['label'] = prev_label

        # Saving the figure (optional)
        if save_fig:
            save_filename = os.path.join(save_dir, 'Feynman' + type + '_fitting.png') 
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')

        # Displaying the plot (optional)
        if show_plot:
            plt.show()