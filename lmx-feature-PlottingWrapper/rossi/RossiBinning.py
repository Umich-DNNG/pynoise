# local imports
from lmx.Event import Event
# standard imports
from typing import List
import numpy as np
import bisect
import sys

sys.path.append(r"C:\Users\352798\python")


class RossiBinningTypeI:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type I Binning: Window shifts and takes time difference for every neutron in list

            Arguments:
                events: list of Event types
                reset_time: window (in nanoseconds)
                bins: number of bins to split up the window

            Returns:
                hist: unprocessed frequencies of time differences
        """
        if not events:
            raise ValueError("Must provide a list of Events")
        if reset_time <= 0:
            raise ValueError("reset time must be greater than 0")
        if bins <= 0:
            raise ValueError("Bin quantity must be greater than 0")

        bin_width = reset_time / bins
        limit = bins * 3
        hist = [0] * bins  # initialize time diff array
        times = [event.time for event in events]
        # Type I
        for now, current in enumerate(times):
            shift_reset = current + reset_time
            shift_limit = now + limit

            if shift_limit < len(times):
                pos_guess = bisect.bisect_left(times, shift_reset, lo=now, hi=shift_limit)
                for time in times[now + 1: pos_guess]:
                    digit = int((time - current) / bin_width)
                    hist[digit] += 1
        return hist


class RossiBinningTypeII:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type II Binning: Window shifts and takes time difference for every neutron after previous window

            Arguments:
                events: list of Event types
                reset_time: window (in nanoseconds)
                bins: number of bins to split up the window

            Returns:
                hist: unprocessed frequencies of time differences
        """
        if not events:
            raise ValueError("Must provide a list of Events")
        if reset_time <= 0:
            raise ValueError("reset time must be greater than 0")
        if bins <= 0:
            raise ValueError("Bin quantity must be greater than 0")

        bin_width = reset_time / bins
        limit = bins * 3
        hist = [0] * bins  # initialize time diff array
        times = [event.time for event in events]
        now = 0
        while now < len(times):
            shift_reset = times[now] + reset_time
            shift_limit = now + limit
            if shift_limit > len(times):
                pos_guess = bisect.bisect_left(times, shift_reset, lo=now + 1, hi=shift_limit)
                for time in times[now + 1: pos_guess]:
                    digit = int((time - times[now]) / bin_width)
                    hist[digit] += 1
                now = (pos_guess + 1)
        return hist


class RossiBinningTypeIII:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type III Binning: Time difference between even and odd events in a list

            Arguments:
                events: list of Event types
                reset_time: window (in nanoseconds)
                bins: number of bins to split up the window

            Returns:
                hist: unprocessed frequencies of time differences
        """
        if not events:
            raise ValueError("Must provide a list of Events")
        if reset_time <= 0:
            raise ValueError("reset time must be greater than 0")
        if bins <= 0:
            raise ValueError("Bin quantity must be greater than 0")

        bin_width = reset_time / bins
        hist = [0] * bins  # initialize time diff array
        times = [event.time for event in events]
        b = times[1::2]
        a = times[0::2]
        td_hold = [int((b_i - a_i) / bin_width) for a_i, b_i in zip(a, b)]
        for hist_bin in range(bins):
            hist[hist_bin] += td_hold.count(hist_bin)
        return hist
