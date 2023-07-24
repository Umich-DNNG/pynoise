import numpy as np
import Event as evt
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os


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



    def randomCounts(self, triggers: list[evt.Event], tau: int):

        '''Converts a list of Events into random trigger gate frequencies.
        
        Requires:
        - triggers: the list of Events. Assumes the 
        list is sorted from least to greatest time.
        - tau: the gate width.'''

        # Convert the list of times into gate indices.
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
                frequencies[0] += cur - prev - 1
                # Reset variables.
                count = 1
                prev = cur
        if count != 1:
            while count > len(frequencies)-1:
                frequencies.append(0)
            frequencies[count] += 1    
        # Get number of non-empty gates and convert frequencies into probabilities.
        num_gates = sum(frequencies)
        frequencies = [freq/num_gates for freq in frequencies]
        # Return probability list.
        return frequencies


    def FeynmanY_histogram(self,
                           probabilities, 
                           show_plot: bool = False,  
                           save_fig: bool = False, 
                           save_dir: str = './',
                           hvs: dict = None):

        '''Creates a histogram from a numpy array of random trigger probabilities .
        
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


    def computeVarToMean(self, probabilities, tau):

        '''Creates the two moments from probabilities.
        
        Requires:
        - probabilities (numpy array): index representing the bin count, and value representing frequency
        '''

        moment1 = 0
        moment2 = 0
        for i in range(len(probabilities)):
            moment1 += (i)*probabilities[i]
            moment2 += (i)*(i-1)*probabilities[i]
        moment2 /= 2
        return (2*moment2 + moment1 - moment1*moment1)/moment1 - 1, (moment2 - moment1*moment1/2)/(tau*1e-9)


    def plot(self, taus, ys, save_fig, show_plot, save_dir):
        
        plt.plot(taus,ys)

        # Saving the figure (optional)
        if save_fig:
            save_filename = os.path.join(save_dir, 'FeynmanY.png') 
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
            
        # Displaying the plot (optional)
        if show_plot:
            plt.show()

        plt.show()


    def fitting(self, x_data, y_data, gamma_guess, alpha_guess):

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

        # Plot the original data points and the fitted curve
        plt.scatter(x, y, label='Data')
        plt.plot(x_fit, self.pred, color='red', label='Fitted Curve')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.show()