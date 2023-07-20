# standard imports
from typing import List

# third party imports

# local imports
from lmx.Event import Event
from lmx.Header import Header

class LMXFile :
    
    def __init__( self, header : Header , events : List[ Event ] ) :
        
        self.events = events
        self.header = header
    
    @property
    def header( self ) :
        
        return self._header
    
    @header.setter
    def header( self, header : Header ) :
        
        self._header = header
        
    @property
    def events( self ) :
        
        return self._events
        
    @events.setter
    def events( self, events  : List[ Event ] ) :
        
        self._events = events
        self._maxDetector = max( [ event.detector for event in self.events ] )
          
    def detectorEvents( self, detector : int ) :
        
        return [ event for event in self.events if event.detector == detector ]
    
    def detectorCounts( self, detector : int ) :
        
        return len( self.detectorEvents( detector ) ) 
    
    def allDetectorCounts( self ) :
        
        detectors = { i : 0 for i in range( 1, self._maxDetector + 1 ) }
        for event in self.events :
            
            detectors[ event.detector ] += 1
            
        return detectors
    