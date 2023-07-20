# standard imports

# third party imports

# local imports

class Event :
    """Class that a single detector event, it contains a time value and
       detector identifier"""

    def __eq__( self, right ) :
        """Comparison function for testing purposes"""

        if isinstance( right, type( self ) ) :

            return ( ( self.detector == right.detector ) and
                     ( self.time == right.time ) )

        return NotImplemented

    def __init__( self, detector : int, time : float ):
        """Initialise the event using the detector index and time value

           Arguments:
               detector : the detector index of the detector to which the
                          detector event relates
               time : the time value

           Exceptions:
               ValueError : something went wrong
        """

        self.detector = detector
        self.time = time

    @property
    def detector( self ) :
        """Return the detector index of the event"""

        return self._detector

    @detector.setter
    def detector( self, detector : int ) :
        """Set the detector index of the event"""

        if detector < 0 :

            raise ValueError( 'The detector index cannot be negative.' )

        self._detector = detector

    @property
    def time( self ) :
        """Return the time value of the event"""

        return self._time

    @time.setter
    def time( self, time : float ) :
        """Set the time value of the event"""

        if time < 0 :

            raise ValueError( 'The time cannot be negative.' )

        self._time = time

    def __str__( self ) :

        return ( 'An event occurred at ' + str( self.time )
                 + ' seconds in detector ' + str( self.detector ) )

    def __repr__( self ) :

        return '(' + str( self.detector ) + ',' + str( self.time ) + ')'
