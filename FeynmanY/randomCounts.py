import numpy as np
import Event as evt

def randomCounts(triggers: list[evt.Event], tau: int):
    # Get the smallest time measurement to mark as the beginning.
    min_time = triggers[0].time
    # Convert the list of times into which gate each measurement is in.
    triggers = (np.array([(event.time - min_time)/tau for event in triggers])).astype(int)
    frequencies = []
    count = 1
    prev = triggers[0]
    for measurement in triggers[1:]:
        if measurement == prev:
            count += 1
        else:
            while count > len(frequencies):
                frequencies.append(0)
            frequencies[count-1] += 1
            count = 1
        prev = measurement
    num_gates = sum(frequencies)
    frequencies = [freq/num_gates for freq in frequencies]
    return frequencies