import numpy as np
import Event as evt
import matplotlib.pyplot as plt
import os

def randomCounts(triggers: list[evt.Event], tau: int):

    '''Converts a list of Events into random trigger gate frequencies.
    
    Requires:
    - triggers: the list of Events. Assumes the 
    list is sorted from least to greatest time.
    - tau: the gate width.'''

    # Get the smallest time measurement to mark as the beginning.
    min_time = triggers[0].time
    # Convert the list of times into gate indices.
    triggers = (np.array([(event.time - min_time)/tau for event in triggers])).astype(int)
    frequencies = []
    count = 1
    prev = triggers[0]
    # For all measurements:
    for measurement in triggers[1:]:
        # If still in the same gate, increment the count.
        if measurement == prev:
            count += 1
        else:
            # If count index doesn't currently 
            # exist, append zeros until it does.
            while count > len(frequencies):
                frequencies.append(0)
            # Increase the frequency for the count index.
            frequencies[count-1] += 1
            # Reset variables.
            count = 1
            prev = measurement
    # Get number of non-empty gates and convert frequencies into probabilities.
    num_gates = sum(frequencies)
    frequencies = [freq/num_gates for freq in frequencies]
    # Return probability list.
    return frequencies


def FeynmanY_histogram(probabilities, show_plot, save_fig, save_dir):

    '''Creates a histogram from a numpy array of random trigger probabilities .
    
    Requires:
    - triggers: the list of Events. Assumes the 
    list is sorted from least to greatest time.
    - tau: the gate width.'''

    bins = np.arange(len(probabilities))
    values = probabilities

    # Plot histogram using plt.bar
    plt.bar(bins, values, align='center', width=0.8)

    # Currently harded coded to be in log scale
    plt.yscale('log')

    # Customize plot if needed
    plt.xlabel('r')
    plt.ylabel('Pn*')
    plt.title('FeynmanY Random Trigger')

    # Saving the figure (optional)
    if save_fig:
        os.path.join(save_dir, 'FeynmanY.png') 
        
    # Displaying the plot (optional)
    if show_plot:
        plt.show()



#------- HARD CODE SECTION (TESTING) ------------------#

test = evt.createEventsListFromTxtFile(filePath='/Users/vincentweng/Documents/PyNoise/RossiAlpha/sample_data/RF3-40_59min.txt', timeCol = 0, channelCol = None)

test.sort(key=lambda Event: Event.time)

counts = randomCounts(triggers=test, tau=1000)

FeynmanY_histogram(counts, show_plot = False, save_fig = True, save_dir="./")

#------------------------------------------------------#