# standard imports

# third party imports

# local imports

class ValueUnit :

    #If two values or units have the same information, but are in different
    #locations, the values/units are the same:
    def __eq__( self, right ) :

        #The events should be the same type:
        if isinstance( right, type( self ) ) :

            return ( ( self.value == right.value ) and
                     ( self.unit == right.unit ) )

        #The events aren't the same type, but this isn't dealt with:
        return NotImplemented

    def __init__( self, value : float, unit : str ) :

        self.value = value
        self.unit = unit

    @property
    def value( self ) :

        return self._value

    @value.setter
    def value( self, value : float ) :

        if value == None :

            raise ValueError( 'The value cannot be undefined.' )

        self._value = value

    @property
    def unit( self ) :

        return self._unit

    @unit.setter
    def unit( self, unit : str ) :

        if unit == None :

            raise ValueError( 'The unit cannot be undefined.' )

        self._unit = unit
