import numpy as np
import Event as evt

def randomCounts(triggers: list[evt.Event], tau: int):
    # Get the total number of gates.
    num_gates = int(np.ceil(triggers[len(triggers)-1]/tau))
    # Convert the list of times into which gate each measurement is in.
    gates = (np.array([event.time for event in triggers]) / tau).astype(int)
    # Count the number of measurements in each gate and then count the frequency of each size.
    frequencies = np.bincount(np.bincount(gates))
    # Converts the counts into probabilities.
    probabilities = (np.array([frequency/num_gates for frequency in frequencies]))
    # Return the list.
    return probabilities