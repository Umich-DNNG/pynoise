# standard imports
from scipy.stats import poisson as poissiondist
import matplotlib.pyplot as plt
import numpy
import math


class FeynmanHistogram:

    def __init__(self, gatewidth: float, frequency: list):
        """Initialise the Feynman histogram

            Arguments:
               gatewidth : the gate width (often referred to as tau, has to be
                           given in nanoseconds)
               frequency : the count frequency (unnormalized) for all gates
                           (the sum of this list is the total number N of gates)

            Exceptions:
               ValueError : Something is wrong with the data (no counts, zero
                            or negative gate width, etc.)
        """
        if (not isinstance(gatewidth, float) and not isinstance(gatewidth, int)) or gatewidth <= 0.:
            raise ValueError('The gate width cannot be zero or negative.')
        else:
            self.gatewidth = float(gatewidth)

        if not frequency or not isinstance(frequency, list):
            raise ValueError('The frequency cannot be undefined or empty.')
        else:
            self.frequency = frequency
        self.number_gates = int(sum(self.frequency))
        self.normalized_frequency = [frequency / self.number_gates
                                     for frequency in self.frequency]

        self._factorial = {}
        self._reduced_factorial = {}
        self._count_rate = {}

    @property
    def gatewidth(self):
        """Retrieve gatewidth

            Returns: Gatewidth in nanoseconds
        """

        return self._gatewidth

    @gatewidth.setter
    def gatewidth(self, gatewidth: float):
        """Sets gatewidth

            Arguments:
                gatewidth: Gatewidth in nanoseconds
        """
        if (not isinstance(gatewidth, float) and not isinstance(gatewidth, int)) or gatewidth <= 0.:
            raise ValueError('The gate width cannot be zero or negative.')

        self._gatewidth = float(gatewidth)

    @property
    def frequency(self):
        """Retrieve frequency of binning

            Returns: Frequency for the pre-specified gatewidth
        """
        return self._frequency

    @frequency.setter
    def frequency(self, frequency: list):
        """Sets frequency

            Arguments:
                frequency: Frequency of a Feynman binning result
        """
        if not frequency or not isinstance(frequency, list):
            raise ValueError('The frequency cannot be undefined or empty.')

        self._frequency = frequency

    @property
    def number_gates(self):
        """Retrieve number of gates

            Returns: number of gates
        """
        return self._number_gates

    @number_gates.setter
    def number_gates(self, number_gates: int):
        """Sets number of gates

            Arguments:
                number_gates: number of gates
        """
        if not isinstance(number_gates, int) or number_gates <= 0:
            print(number_gates)
            raise ValueError('The number of gates cannot be zero or negative.')

        self._number_gates = number_gates

    @property
    def normalized_frequency(self):
        """Retrieve normalized frequency of binning

            Returns: Normalized frequency for the pre-specified gatewidth
        """
        return self._normalized

    @normalized_frequency.setter
    def normalized_frequency(self, normalized: list):
        """Sets normalized frequency

            Arguments:
                normalized: Normalized frequency of a Feynman binning result
        """
        if not normalized or not isinstance(normalized, list):
            raise ValueError('The normalized frequency cannot be undefined '
                             + 'or empty.')

        self._normalized = normalized

    def reduced_factorial_moment(self, order: int):
        """Calculate the reduced factorial moments m (equations 2-6)

            Arguments:
                order: the order of the reduced factorial moment (r in
                       equation 2-6)
        """
        if not order in self._reduced_factorial:
            def notImplemented(self, order):
                raise NotImplementedError('Order ' + str(order) + ' not '
                                          + 'implemented for reduced factorial '
                                          + 'moment')

            switcher = {

                1: lambda self, order: self.factorial_moment(1),
                2: lambda self, order: (self.factorial_moment(2) -
                                        self.factorial_moment(1)) / 2.,
                3: lambda self, order: (self.factorial_moment(3) -
                                        3. * self.factorial_moment(2) +
                                        2. * self.factorial_moment(1)) / 6.,
                4: lambda self, order: (self.factorial_moment(4) -
                                        6. * self.factorial_moment(3) +
                                        11. * self.factorial_moment(2) -
                                        6. * self.factorial_moment(1)) / 24.
            }

            self._reduced_factorial[order] = switcher.get(order, notImplemented)(self, order)

        return self._reduced_factorial[order]

    def factorial_moment(self, order: int):
        """Calculate the factorial moments Cbar (equations 7-11)

            Arguments:
                order : the order of the factorial moment (r in equation 7-11)
        """
        if not order:
            raise ValueError("Real integer must be provided")
        if not order in self._factorial:
            npower = [pow(n, order)
                      for n in range(len(self.normalized_frequency))]
            self._factorial[order] = numpy.inner(npower, self.normalized_frequency)

        return self._factorial[order]

    @property
    def mean(self):
        """Retrieves the first factorial moment; the mean

            Returns: Mean for the gate width
        """
        return self.factorial_moment(1)

    @property
    def variance(self):
        """Retrieves the second factorial moment; the variance

            Returns: Variance for the gate width
        """
        return self.factorial_moment(2)

    @property
    def variance_to_mean(self):
        """Calculates variance to mean ratio

            Returns: Variance to mean ratio
        """
        mean = self.mean
        variance = self.variance
        return (variance - mean * mean) / mean - 1.0

    @property
    def Y1(self):
        """Calculates Y1 for the gatewidth

            Returns:
                y1: Y1 value for the gatewidth
                dy1: Error on the Y1 value
        """
        m1 = self.reduced_factorial_moment(1)
        m2 = self.reduced_factorial_moment(2)
        tau = self.gatewidth * 1e-9
        N = self.number_gates
        
        y1 = m1 / tau
        dy1 = math.sqrt((2. * m2 + m1 * (1. - m1)) / (N - 1)) / tau
        return (y1, dy1)

    @property
    def Y2(self):
        """Calculates Y2 for the gatewidth

            Returns:
                y2: Y2 value for the gatewidth
                dy2: Error on the Y2 value
        """
        m1 = self.reduced_factorial_moment(1)
        m2 = self.reduced_factorial_moment(2)
        m3 = self.reduced_factorial_moment(3)
        m4 = self.reduced_factorial_moment(4)
        tau = self.gatewidth * 1e-9
        N = self.number_gates
        
        y2 = (m2 - m1 * m1 / 2.) / tau
#        if (6. * m4 + 6. * m3 + m2 * (1. - m2)) > 0:
#            dy2 = math.sqrt((6. * m4 + 6. * m3 + m2 * (1. - m2)) / (N - 1)) / tau
        # Equation 29 instead of Equation 25
        if (6*m4-6*m3*m1+6*m3-m2**2+4*m2*m1**2-4*m2*m1+m2-m1**4+m1**3) > 0:
            dy2 = math.sqrt((6*m4-6*m3*m1+6*m3-m2**2+4*m2*m1**2-4*m2*m1+m2-m1**4+m1**3) / (N - 1)) / tau
        else:
            dy2 = 0
        return (y2, dy2)

    # covariance dY1Y2 may need to be included

    def R1(self, decay_constant: float):
        """Calculates R1 for the gatewidth

            Arguments:
                decay_constant: estimated decay constant for nuclear assembly

            Returns: R1 which is equal to Y1
        """
        if not isinstance(decay_constant, float) and not isinstance(decay_constant, int):
            raise ValueError("Decay constant must be a real float")
        return self.Y1[0]

    def R2(self, decay_constant: float):
        """Calculates R2 for the gatewidth

            Arguments:
                decay_constant: estimated decay constant for nuclear assembly

            Returns: R2 which is equal to Y2 divided by the single log equation
                     at the pre-specified gatewidth
        """
        if not isinstance(decay_constant, float) and not isinstance(decay_constant, int):
            raise ValueError("Decay constant must be a real float")
        factor = decay_constant * self.gatewidth
        omega = 1 - (1 - math.exp(-factor)) / factor

        return self.Y2[0] / omega

    def plotHistogram(self, poisson=True, show=True, limit_step=False, save=False, log=False, xmin=False, xmax=False, ymin=False, ymax=False, normalize=False, title=False):
        """ Plots frequency against multiplets for the pre-specified gatewidth

            Arguments:
                poisson: Applies a poisson distribution on top of the histogram
                show: Defaults to displaying the figure

            Returns:
                figure: Variable containing the Feynman figure
                axis: Variable used to control the Feynman figure
        """
        
        # if type(xmin) == int or type(xmin) == float:
        #     x = range(0, int(xmax))
        # else:
        x = range(0, len(self.frequency))
        y = self.frequency
        names = [str(value) for value in x]
        
        if normalize == True:
            y = [element/self.number_gates for element in y]
            y_no_zero = [element for element in y if element != 0]
        
        if len(x) > len(y):
            while len(x) > len(y):
                y.append(0)

        figure, axis = plt.subplots()

        axis.set_xlabel('Multiplet, n')
        if normalize == True:
            axis.set_ylabel('Probability, pn')
        else:
            axis.set_ylabel('Frequency, Cn')
        axis.bar(x, y, alpha=0.5, width=0.8, tick_label=names)
        
        #xmin_data, xmax_data = axis.get_xlim()
        if normalize == True:
            ymin_data = numpy.min(y_no_zero)
            ymax_data = numpy.max(y)
        else:
            ymin_data, ymax_data = axis.get_ylim()
        
        if title != False:
            plt.title(title)
        
        # The 10 here is somewhat arbitrary, but this ensures that the x-axis doesn't have so many ticks that it is unreadable.
        step_limit = 10
        if limit_step == True and len(x) > step_limit:
            if type(xmin) == int or type(xmin) == float:
                axis.set_xticks(numpy.arange(0,xmax, step=int(xmax/step_limit)))
            else:
                axis.set_xticks(numpy.arange(0,x[len(x)-1], step=int(x[len(x)-1]/step_limit)))

        if poisson:
            mean = self.mean
            if normalize == True:
                distribution = poissiondist.pmf(x, mean)
            else:
                distribution = [self.number_gates * value for value in poissiondist.pmf(x, mean)]
            axis.plot(x, distribution, 'r-')
            #xmin_pos, xmax_pos = axis.get_xlim()
            ymin_pos, ymax_pos = axis.get_ylim()
        
        if type(xmin) == int or type(xmin) == float:
            axis.set_xlim(left=xmin, right=xmax)
            axis.set_ylim(top=ymax)
        else:
            axis.set_ylim(top=numpy.max([ymax_data,ymax_pos]))
        
        if log == True:
            axis.set_yscale("log")
            if normalize == True:
                if type(xmin) == int or type(xmin) == float:
                    axis.set_ylim(bottom=ymin)
                else:
                    axis.set_ylim(bottom=ymin_data)
            else:
                axis.set_ylim(bottom=1e-1)
                
        else:
            if type(xmin) == int or type(xmax) == float:
                axis.set_ylim(bottom=ymin)
            else:
                axis.set_ylim(bottom=ymin_data)
        
        if save != False and type(save) == str:
            plt.savefig(save+'_'+str(self.gatewidth)+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+'_'+str(self.gatewidth)+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

        if show:
            figure.show()
        else:
            figure.clear()

        return figure, axis, x, y, distribution
