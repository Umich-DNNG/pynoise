# standard imports
import numpy as np
import matplotlib.pyplot as plt
from typing import List

class RossiHistogram:
    def __init__(self, reset_time: float, frequency: List[float]):
        """Initialise the Rossi histogram processing functions

            Arguments:
                reset_time: the window size (in nanoseconds) where events are compared
                frequency : the solved Rossi-alpha histogram frequency distribution
            
            Exceptions:
                ValueError : Something is wrong with the data (no counts, zero or negative window, etc.)
        """
        if (not isinstance(reset_time, float) and not isinstance(reset_time, int)) or reset_time <= 0:
            raise ValueError("The number of bins must be a non-zero, non-negative float.")
        else:
            self._reset_time = float(reset_time)

        if not frequency or not isinstance(frequency, list):
            raise ValueError("The frequency cannot be an empty list or None.")
        else:
            self._freq = frequency
        self._num_bins = len(frequency)
        self._bins = list(
            np.linspace(reset_time / (2 * self._num_bins), reset_time - (reset_time / (2 * self._num_bins)),
                        self._num_bins))

    def __copy__(self):
        return RossiHistogram(self.reset_time, self.frequency)

    @property
    def reset_time(self):
        """Retrieves reset time
        
            Returns: reset time in nanoseconds
        """
        return self._reset_time

    @reset_time.setter
    def reset_time(self, reset_time: float or int):
        """Sets the reset time
        
            Arguments:
                reset_time:The reset time in nanoseconds
        """
        if (not isinstance(reset_time, float) or not isinstance(reset_time, int)) or reset_time <= 0:
            raise ValueError("The number of bins must be a non-zero, non-negative float.")
        self._reset_time = float(reset_time)

    @property
    def frequency(self):
        """Retrieves the frequency from the pre-specified rest_time and bins

            Returns: The frequency
        """
        return self._freq

    @frequency.setter
    def frequency(self, frequency: List[float]):
        """Sets the amount of frequency

            Arguments:
                frequency: The frequency
        """
        if not frequency or not isinstance(frequency, list):
            raise ValueError("The frequency cannot be an empty list or None.")

        self._freq = frequency
        self._num_bins = len(frequency)

    @property
    def number_bins(self):
        """Retrieves the amount of bins 
        
            Returns: The amount of bins
        """
        return self._num_bins

    @number_bins.setter
    def number_bins(self, num_bins: int):
        """Sets the amount of bins
        
            Arguments:
                num_bins: The amount of bins
        """
        if not isinstance(num_bins, int) or num_bins <= 0:
            raise ValueError("The number of bins must be a non-zero, non-negative integer.")
        self._num_bins = num_bins

    @property
    def bins(self):
        """Retrieves the list of bins
        
            Returns: The list of bins
        """
        return self._bins

    @bins.setter
    def bins(self, bins: List[float]):
        """Sets the list of bins
        
            Arguments:
                bins: The list of bins
        """
        if not bins or (not isinstance(bins, np.ndarray) and not isinstance(bins, list)):
            raise ValueError("The bins cannot be an empty list.")
        self._bins = bins
        self._num_bins = len(bins)


    def plotHistogram(self, show=True, equation: callable = None, parameters: list = None):
        """Creates a plot of the Rossi-alpha distribution
           Includes option to overlay with a user specified equation

            Arguments:
                show: Defaults to displaying the figure
                equation: A callable function
                parameters: List of parameters to represent equation
    
            Returns:
                    figure: Variable containing the Rossi figure
                    axis : Variable used to control aspects of the Rossi figure
        """
        figure, axis = plt.subplots()
        axis.plot(self.bins, self.frequency, label="Raw Calculation", color='#00aaffff',
                  linestyle="-", drawstyle='steps-mid', linewidth=2)
        axis.set_xlabel('Time Difference [ns]', fontsize=16)
        axis.set_ylabel('Counts', fontsize=16)

        if equation and parameters:
            result = equation(self.bins, *parameters)
            axis.plot(self.bins, result, label="User equation",
                      color='k', linestyle="--", linewidth=2)

        axis.legend()
        figure.tight_layout()
        if show:
            figure.show()

        return figure, axis
>>>>>>> 132c7fd07defd957fc168e57ce7f7e3edf306102
