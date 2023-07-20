# standard imports
import time
from typing import List, Callable
import bisect

import numpy
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
# third party imports

# local imports
from lmx.Event import Event

class SequentialBinning:

    def __init__(self):
        pass

    def __call__(self, events: List[Event], gatewidth: float):
        print("Sequential Binning Started")
        if not events:
            raise ValueError("Must provide a list of Events")
        if gatewidth <= 0:
            raise ValueError("gatewidth must be greater than 0")

        gates = (np.array([event.time for event in events]) / gatewidth).astype(int)
        max_gate = bisect.bisect_left(gates, gates[-1])
        last_gate = np.searchsorted(gates[:max_gate], list(range(gates[max_gate])), side="right")

        frequency = np.bincount(last_gate[1:] - last_gate[:-1])
        frequency[last_gate[0]] += 1

        return list(frequency)

class SequentialBinning_old:

    def __init__(self):
        pass

    def __call__(self, events: List[Event], gatewidth: float):
        frequency = {0: 0}
        count = 0
        current = 0
        gates = (np.array([event.time for event in events]) / gatewidth).astype(int)
        max_gate_position = bisect.bisect_left(gates, gates[-1])
        for gate in tqdm(gates[:max_gate_position]):
        # for event in tqdm(events):

            # gate = int(event.time / gatewidth)
            if gate == current:

                count += 1

            else:

                # the gates before the current event have no hits
                frequency[0] += gate - current - 1

                # increment the frequency count for the current gate
                if count not in frequency: frequency[count] = 0
                frequency[count] += 1

                # reset the current gate and set the number of counts to one
                current = gate
                count = 1

        # account for the last gate
        # if count not in frequency: frequency[count] = 0
        # frequency[count] += 1
        return [frequency.get(count, 0)
                for count in range(max(frequency.keys()) + 1)]