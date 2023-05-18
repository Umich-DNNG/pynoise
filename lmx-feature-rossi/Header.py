# standard imports
from typing import Dict

# third party imports

# local imports
from lmx.ValueUnit import ValueUnit

class Header :

    def __init__( self, ticklength : ValueUnit, MsmtDuration : ValueUnit,
                 AvgCountRate : ValueUnit, FaceToSource : ValueUnit,
                 CenterToFloor : ValueUnit, FifoLostCounts: int, RR12 : float,
                 RR13 : float, RR23 : float, other : Dict ):

        self.ticklength = ticklength
        self.MsmtDuration = MsmtDuration
        self.AvgCountRate = AvgCountRate
        self.FaceToSource = FaceToSource
        self.CenterToFloor = CenterToFloor
        self.FifoLostCounts = FifoLostCounts
        self.RR12 = RR12
        self.RR13 = RR13
        self.RR23 = RR23

        self.other = other

    @property
    def ticklength( self ) :

        return self._ticklength

    @ticklength.setter
    def ticklength( self, ticklength : ValueUnit ) :

        self._ticklength = ticklength

    @property
    def MsmtDuration( self ) :

        return self._MsmtDuration

    @MsmtDuration.setter
    def MsmtDuration( self, MsmtDuration : ValueUnit ) :

        self._MsmtDuration = MsmtDuration

    @property
    def AvgCountRate( self ) :

        return self._AvgCountRate

    @AvgCountRate.setter
    def AvgCountRate( self, AvgCountRate : ValueUnit ) :

        self._AvgCountRate = AvgCountRate

    @property
    def FaceToSource( self ) :

        return self._FaceToSource

    @FaceToSource.setter
    def FaceToSource( self, FaceToSource : ValueUnit ) :

        self._FaceToSource = FaceToSource

    @property
    def CenterToFloor( self ) :

        return self._CenterToFloor

    @CenterToFloor.setter
    def CenterToFloor( self, CenterToFloor : ValueUnit ) :

        self._CenterToFloor = CenterToFloor

    @property
    def FifoLostCounts( self ) :

        return self._FifoLostCounts

    @FifoLostCounts.setter
    def FifoLostCounts( self, FifoLostCounts : ValueUnit ) :

        self._FifoLostCounts = FifoLostCounts

    @property
    def RR12( self ) :

        return self._RR12

    @RR12.setter
    def RR12( self, RR12 : float ):

        self._RR12 = RR12

    @property
    def RR13( self ) :

        return self._RR13

    @RR13.setter
    def RR13( self, RR13 : float ):

        self._RR13 = RR13

    @property
    def RR23( self ) :

        return self._RR23

    @RR23.setter
    def RR23( self, RR23 : float ):

        self._RR23 = RR23

    @property
    def other( self ) :

        return self._other

    @other.setter
    def other( self, other : Dict ):

        self._other = other
