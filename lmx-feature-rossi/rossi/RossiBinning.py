# local imports
import multiprocessing

import pandas
from lmx.Event import Event
# standard imports
import matplotlib.pyplot as plt
from multiprocessing import Pool, freeze_support
from typing import List
from tqdm import tqdm
import numpy as np
import bisect
from numba import njit, prange
import pandas


def RossiBinningError(events: List[Event], reset_time: float, bins: int):
    if not events:
        raise ValueError("Must provide a list of Events")
    if reset_time <= 0:
        raise ValueError("reset time must be greater than 0")
    if bins <= 0:
        raise ValueError("Bin quantity must be greater than 0")

def RossiPreBinning(events: List[Event], reset_time: float, bins: int):
    bin_width = float(reset_time) / bins
    histogram_starter = [0]*bins
    times_list = np.array([event.time for event in events]) / bin_width
    return histogram_starter, times_list, bins

class RossiBinningTypeI:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type I Binning: Window shifts and takes time difference for every event in list

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

        RossiBinningError(events, reset_time, bins)
        hist, times, bins = RossiPreBinning(events, reset_time, bins)
        pos_guess=0

        # Find right edge of time list where calculations are possible
        last_spot = bisect.bisect_right(times, times[-1] - bins)

        # Type I
        print("Type 1 Binning Begins:")
        for now, current in enumerate(tqdm(times[:last_spot])):
            pos_guess = bisect.bisect_left(times, current + bins, lo=pos_guess)
            try:
                hist += np.bincount((times[now + 1:pos_guess] - current).astype(int), minlength=bins)
            except:
                print(" Note: A time jump greater than the reset time occured. "
                      "The program will attempt to continue.")
                try:
                    hist += np.bincount((times[now + 1:pos_guess] - current).astype(int), minlength=bins)[:bins]
                except:
                    pass

        return list(hist)

class RossiBinningTypeII:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type II Binning: Window shifts and takes time difference for every event after previous window

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

        RossiBinningError(events, reset_time, bins)
        hist, times = RossiPreBinning(events, reset_time, bins)

        # Find right edge of time list where calculations are possible
        last_window = int(times[-1] / bins) - 1
        last_spot = -1
        while last_window < (times[last_spot] / bins):
            last_spot -= 1

        # Type II
        print("Type 2 Binning Begins:")
        now = 0
        while now <= last_spot:
            current = times[now]
            pos_guess = bisect.bisect_left(times, current + bins, lo=pos_guess)
            try:
                hist += np.bincount((times[now + 1: pos_guess] - current).astype(int), minlength=bins)
            except:
                pass
            now = (pos_guess + 1)

        return list(hist)


class RossiBinningTypeIII:
    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Type III Binning: Time differences between even and odd events in a list

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

        RossiBinningError(events, reset_time, bins)
        hist, times = RossiPreBinning(events, reset_time, bins)

        b = times[1::2]
        a = times[0::2]
        td_hold = b[:len(a)-1] - a
        hist = np.bincount(td_hold.astype(int), minlength=bins)

        return list(hist[:bins])


class TimeIntervalAnalysis:

    def __init__(self):
        pass

    def __call__(self, events: List[Event], reset_time: float, bins: int):
        """ Time Interval Analysis: Time differences between one event and its previous event for every event

            Arguments:
                events: list of Event types
                reset_time: window (in nanoseconds)
                bins: number of bins to split up the window

            Returns:
                hist: unprocessed frequencies of time differences
        """
        RossiBinningError(events, reset_time, bins)
        hist, times = RossiPreBinning(events, reset_time, bins)
        hists = np.bincount(np.absolute(np.subtract.accumulate(times)), minlength=bins)

        return list(hists[:bins])
