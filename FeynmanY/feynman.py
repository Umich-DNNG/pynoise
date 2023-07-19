import numpy as np
import Event as evt
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import os

def YFit(gamma, alpha, tau):
    return gamma*(1+(1-np.exp(alpha*tau))/(alpha*tau))

def randomCounts(triggers: list[evt.Event], tau: int):

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
    while count > len(frequencies)-1:
        frequencies.append(0)
    # Increase the frequency for the count index.
    frequencies[count] += 1
    if cur != prev:
        frequencies[0] += cur - prev - 1
    # Get number of non-empty gates and convert frequencies into probabilities.
    num_gates = sum(frequencies)
    frequencies = [freq/num_gates for freq in frequencies]
    # Return probability list.
    return frequencies


def FeynmanY_histogram(probabilities, scale: str, 
                       show_plot: bool, 
                       save_fig: bool, 
                       save_dir: str,
                       hvs: dict):

    '''Creates a histogram from a numpy array of random trigger probabilities .
    
    Requires:
    - triggers: the list of Events. Assumes the 
    list is sorted from least to greatest time.
    - tau: the gate width.'''

    bins = np.arange(len(probabilities))
    values = probabilities

    # Plot histogram using plt.bar
    plt.bar(bins, values, align='center', width=0.8,**hvs)
    plt.yscale(scale)
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

def computeVarToMean(probabilities, tau):

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
    return (2*moment2 + moment1 - moment1*moment1)/moment1 - 1, (moment2 - moment1*moment1/2)/tau

def plot(taus, ys, save_fig, show_plot, save_dir):
    
    plt.plot(taus,ys)

    # Saving the figure (optional)
    if save_fig:
        save_filename = os.path.join(save_dir, 'FeynmanY.png') 
        plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
    # Displaying the plot (optional)
    if show_plot:
        plt.show()

    plt.show()


def fitting(x_data, y_data, tau_interval, gamma_guess, alpha_guess):

    # Convert the lists to NumPy arrays
    x = np.array(x_data)
    y = np.array(y_data)

    # Define the initial guesses as a tuple
    initial_guesses = (gamma_guess, alpha_guess)

    # Perform the curve fitting using curve_fit
    popt, pcov = curve_fit(YFit, x, y, p0=initial_guesses)

    # Retrieve the optimized parameters
    gamma_opt, alpha_opt = popt

    # Display the optimized parameters
    print("Optimized gamma:", gamma_opt)
    print("Optimized alpha:", alpha_opt)

    # Generate x values for plotting the fitted curve
    x_fit = np.linspace(min(x), max(x), tau_interval)

    # Generate y values using the fitted parameters
    y_fit = YFit(x_fit, gamma_opt, alpha_opt)

    # Plot the original data points and the fitted curve
    plt.scatter(x, y, label='Data')
    plt.plot(x_fit, y_fit, color='red', label='Fitted Curve')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    plt.show()

def testing():
    data = evt.createEventsListFromTxtFile('/Users/maxtennant/Downloads/internship/pynoise/testing.txt',
                                           0,
                                           None)
    data.sort(key=lambda Event: Event.time)
    print('Tau\tY\t\t\tY2')
    for i in range(1, 21):
        frequencies = randomCounts(data, i/2.0)
        y, y2 = computeVarToMean(frequencies, i/2.0)
        print(str(i/2.0) + '\t' + str(y) + '\t' + str(y2))