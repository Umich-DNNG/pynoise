# standard imports
from typing import List, Callable

# third party imports
import bisect

# local imports
from lmx.Event import Event
from lmx.rossi.RossiBinning import RossiBinningTypeI
from lmx.rossi.RossiHistogram import RossiHistogram


class RossiHistogramCalculator:

    def __init__(self, event_list: List[Event], binning: Callable = RossiBinningTypeI(), time_cutoff=None):
        """ Initialize Rossi Histogram Calculator

            Arguments:
                event_list: List of Event types
                binning: Defaults to Type I binning
                         Type II and III binning also supported
                time_cutoff: Time to cutoff in nanoseconds

            Returns: RossiHistogramCalculator Class type
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

    def calculate(self, reset_time: float, number_bins: int) -> RossiHistogram:
        """ Calculates the Rossi-alpha histogram from events and parameters
            
            Arguments:
                 reset_time: The window size (in nanoseconds) where events are compared
                 number_bins: Divides the window into N bins (should be greater than detector timing)
            
            Returns:
                Initialized RossiHistogram Class for analysis
        """
        return RossiHistogram(reset_time, self._binning(self.events, reset_time, number_bins))
