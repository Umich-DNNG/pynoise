import numpy as np
import Event as evt

def randomCounts(triggers: list[evt.Event], tau: int):
    # Get the smallest time measurement to mark as the beginning.
    min_time = triggers[0]
    num_gates = int(np.ceil((triggers[len(triggers)-1].time-min_time.time)/tau))
    # Convert the list of times into which gate each measurement is in.
    gates = (np.array([(event.time - min_time)/tau for event in triggers])).astype(int)
    # Count the number of measurements in each gate and then count the frequency of each size.
    frequencies = np.bincount(np.bincount(gates))
    # Converts the counts into probabilities.
    probabilities = (np.array([frequency/num_gates for frequency in frequencies]))
    # Return the list.
    return probabilities