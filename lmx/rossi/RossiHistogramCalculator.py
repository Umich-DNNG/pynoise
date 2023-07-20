# standard imports
from typing import List, Callable
import sys

sys.path.append(r"C:\Users\352798\python")

# local imports
# noinspection PyUnresolvedReferences
from lmx.Event import Event
from lmx.rossi.RossiBinning import *
from lmx.rossi.RossiHistogram import *


class RossiHistogramCalculator:

    def __init__(self, event_list: List[Event], binning: Callable = RossiBinningTypeI()):
        """ Initialize Rossi Histogram Calculator

                Arguments:
                    event_list: list of Event types
                    binning   : automatically does Type I binning
                                but II and III binning also supported

                Exceptions: none

                Returns: RossiHistogramCalculator Class type
        """
        self._binning = binning
        self.events = event_list
        self.events.sort(key=lambda event: event.time)

    @property
    def events(self):
        return self._events

    @events.setter
    def events(self, events: List[Event]):
        if not events:
            raise ValueError('The events must be defined and cannot be empty.')

        self._events = events

    def calculate(self, reset_time: float, bin_num: int) -> RossiHistogram:
        """ Calculates the Rossi-alpha histogram from events and parameters

            Args:
                 reset_time: the window size (in nanoseconds) where events are compared
                 bin_num   : divide the window into N bins (should be greater than detector timing)

            Returns:
                Initialized RossiHistogram Class for post processing

        """
        return RossiHistogram(reset_time, self._binning(self.events, reset_time, bin_num))
