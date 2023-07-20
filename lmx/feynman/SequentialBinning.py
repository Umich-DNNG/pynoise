# standard imports
from typing import List, Callable

# third party imports

# local imports
from lmx.Event import Event

class SequentialBinning :

    def __init__( self ) :

        pass

    def __call__( self, events : List[ Event ], gatewidth : float ) :

        frequency = { 0 : 0 }
        count = 0
        current = 0
        for event in events :

            gate = int( event.time / gatewidth )
            if gate == current :

                count += 1

            else :

                # the gates before the current event have no hits
                frequency[ 0 ] += gate - current - 1

                # increment the frequency count for the current gate
                if count not in frequency : frequency[ count ] = 0
                frequency[ count ] += 1

                # reset the current gate and set the number of counts to one
                current = gate
                count = 1

        # account for the last gate
        if count not in frequency : frequency[ count ] = 0
        frequency[ count ] += 1

        return [ frequency.get( count, 0 )
                 for count in range( max( frequency.keys() ) + 1 ) ]
