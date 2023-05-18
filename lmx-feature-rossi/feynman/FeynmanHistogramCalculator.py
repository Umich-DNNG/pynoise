# standard imports
from typing import List, Callable

# third party imports
import bisect

# local imports
from lmx.Event import Event
from lmx.feynman.SequentialBinning import SequentialBinning
from lmx.feynman.FeynmanHistogram import FeynmanHistogram


class FeynmanHistogramCalculator:

    def __init__(self, event_list: List[Event], binning: Callable = SequentialBinning(), time_cutoff: float = None):
        """ Initialize Feynman Histogram Calculator

            Arguments:
                event_list: list of Event types
                binning: automatically does Sequential Binning
                time_cutoff: Time to cutoff in nanoseconds
            
            Exceptions: none
            
            Returns: FeynmanHistogramCalculator Class type
        """

        self._binning = binning
        self._events = event_list
        self._events.sort(key=lambda event: event.time)
        self._timeCutoff = time_cutoff
        if self._timeCutoff:
            cutoff_index = bisect.bisect_left([event.time for event in self.events], self._timeCutoff)
            self.events = self.events[:cutoff_index]

    @property
    def timeCutoff(self):
        """Retrieves the Time Cutoff

        Returns: None or Time Cutoff value
        """
        return self._timeCutoff

    @timeCutoff.setter
    def timeCutoff(self, cutoff: float):
        """Sets the Cutoff Time in nanoseconds

            Arguments:
                cutoff = Value in nanoseconds
        """
        if not cutoff:
            raise ValueError('The Cutoff Time value must be defined')
        self._timeCutoff = cutoff

    @property
    def events(self):
        """Retrieves the list of events

            Returns: List of events
        """
        return self._events

    @events.setter
    def events(self, events: List[Event]):
        """Sets the list of events

            Arguments:
                events: List of events
        """
        if not events:
            raise ValueError('The events must be defined and cannot be empty.')
        self._events = events

    def calculate(self, gatewidth: float) -> FeynmanHistogram:
        """ Calculate a Feynman histogram from the underlying frequencies and the
            user provided gate width

            Arguments:
                gatewidth: The gatewidth in nanoseconds for Feynman Calculation
                disableProgBar: Defaults to printing out the progress bar

            Returns a single Feynman histogram for the given gatewidth
        """

        return FeynmanHistogram(gatewidth, self._binning(self.events, gatewidth))
