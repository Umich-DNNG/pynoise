# standard imports
import matplotlib.pyplot as pyplot
from scipy.stats import poisson as poissiondist
import numpy

# third party imports

# local imports
from lmx.feynman.FeynmanHistogram import FeynmanHistogram

def plot( histogram : FeynmanHistogram, poisson = True ) :

    x = range( 0, len( histogram.frequency ) )
    y = histogram.frequency
    names = [ str( value ) for value in x ]

    pyplot.xlabel( 'Multiplet, n' )
    pyplot.ylabel( 'Frequency, Cn' )
    pyplot.bar( x, y, alpha = 0.5, width = 0.8, tick_label = names )

    if poisson :

        mean = histogram.mean
        distribution = [ histogram.number_gates * value for value in poissiondist.pmf( x, mean ) ]
        pyplot.plot( x, distribution, 'r-' )

    pyplot.show()
