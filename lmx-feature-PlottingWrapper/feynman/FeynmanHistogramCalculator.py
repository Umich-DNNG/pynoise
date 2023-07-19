# standard imports
from typing import List, Callable

# third party imports

# local imports
from lmx.Event import Event
from lmx.feynman.SequentialBinning import SequentialBinning
from lmx.feynman.FeynmanHistogram import FeynmanHistogram

class FeynmanHistogramCalculator :

    def __init__( self, events : List[ Event ], binning : Callable = SequentialBinning() ):

        self._binning = binning
        self.events = events
        self.events.sort( key = lambda event : event.time )

    @property
    def events( self ) :

        return self._events

    @events.setter
    def events( self, events : List[ Event ] ) :

        if not events :

            raise ValueError( 'The events must be defined and cannot be empty.' )

        self._events = events

    def calculate( self, gatewidth : float ) -> FeynmanHistogram :

        return FeynmanHistogram( gatewidth,
                                 self._binning( self.events, gatewidth ) )
